#!/usr/bin/env python

"""
watch events and crd/status
tailing logs from pods of namespace specified
pre-process the input data to text message
and call callback to process the data
"""

import threading, json

from kubernetes import client, config, watch

from config.config import Config
from . mem_queue import MemQueue

def process_log_with_context(mq: MemQueue, callback):
    while True:
        line, meta, context = mq.get()
        callback(line, meta, context)

def tail_log(api, namespace, pod, container, mq, callback):
    w = watch.Watch()
    meta = {"namespace":namespace, "pod":pod, "container": container}

    for line in w.stream(api.read_namespaced_pod_log, name=pod, namespace=namespace, container=container):
        mq.put(line, meta, context={})

class Watcher():
    def __init__(self, config: Config, callback) -> None:
        print("callback is", callback)
        self.callback = callback
        self.threads = {}
        self.num_workers = 1
        self.mq = MemQueue()
        self.create_start_queue_worker()

    def get_key(self, pod: str, container : str):
        return "%s_%s" % (pod, container)

    def start_in_bg(self):
        th = threading.Thread(target=self.start)
        th.start()

    def start(self):
        config.load_kube_config()
        w = watch.Watch()
        v1 = client.CoreV1Api()
        namespaces = set()
        # cnt = 0
        for event in w.stream(v1.list_namespace):
            namespace = event["object"].metadata.name

            if event["type"] == "DELETED":
                print("namespace deleted, stop watching", namespace)
                namespaces.remove(namespace)

                continue
            elif event["object"].status.phase == "Active": 
                # if namespace in namespaces:
                if namespace in namespaces or "cluster-" not in namespace:
                    if namespace != "kube-system":
                        continue
                
                namespaces.add(namespace)
                th = threading.Thread(target=self.watch_namespace, args=(v1, w, namespace))
                th.start()

            # th.join()

    # watch namespace and tail log for each pod
    def watch_namespace(self, client, watch, namespace):
        print("watching namespace", namespace)

        for event in watch.stream(client.list_namespaced_pod, namespace=namespace, watch=True):
            # print("Event: %s %s %s" % (event["type"],event["object"].kind, event["object"].metadata.name))

            podname = event["object"].metadata.name
            containers = []
            for container in event["object"].spec.containers:
                containers.append(container.name)

            if event["type"] == "DELETED":
                for c in containers:
                    th = self.threads.pop(self.get_key(podname, c))
                    print("pod deleted, stop watching ", namespace, podname, c)
                    th._stop()

            elif event["object"].status.phase == "Running":
                for container in containers:
                    key = self.get_key(podname, container)
                    if key not in self.threads:
                        print("start watching", namespace ,podname, container)
                        th = threading.Thread(target=tail_log, args=(client, namespace, podname, container, self.mq, self.callback))
                        self.threads[key] = th
                        th.start()
                        


    # start a new thread to read from the queue and process the lines
    def create_start_queue_worker(self): 
        for i in range(self.num_workers):
            th = threading.Thread(target=process_log_with_context, name="process_log_with_context_watcher", args=(self.mq, self.callback))
            th.start()



if __name__ == "__main__":
    w = Watcher(config=None, callback=print)

    w.start()


