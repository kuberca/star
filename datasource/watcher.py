#!/usr/bin/env python

"""
watch events and crd/status
tailing logs from pods of namespace specified
pre-process the input data to text message
and call callback to process the data
"""

import threading

from kubernetes import client, config, watch

from config.config import Config


def tail_log(api, namespace, pod, container, callback):
    w = watch.Watch()
    meta = {"namespace":namespace, "pod":pod, "container": container}
    for line in w.stream(api.read_namespaced_pod_log, name=pod, namespace=namespace, container=container):
        callback(line, meta)

class Watcher():
    def __init__(self, config: Config, callback) -> None:
        print("callback is", callback)
        self.callback = callback
        self.threads = {}

    def get_key(self, pod: str, container : str):
        return "%s_%s" % (pod, container)

    def start_in_bg(self):
        th = threading.Thread(target=self.start)
        th.start()

    def start(self):
        print()
        config.load_kube_config()
        w = watch.Watch()
        v1 = client.CoreV1Api()
        namespace = "cluster-123"
        for event in w.stream(v1.list_namespaced_pod, namespace=namespace, watch=True):
            print("Event: %s %s %s" % (
                event['type'],
                event['object'].kind,
                event['object'].metadata.name)
            )
            # print(event)
            podname = event['object'].metadata.name
            containers = []
            for container in event['object'].spec.containers:
                containers.append(container.name)

            if event['type'] == "DELETED":
                for c in containers:
                    th = self.threads.pop(self.get_key(podname, c))
            elif event['object'].status.phase == "Running":
                for container in containers:
                    key = self.get_key(podname, container)
                    if key not in self.threads:
                        th = threading.Thread(target=tail_log, args=(v1, namespace, podname, container, self.callback))
                        th.start()
                        self.threads[key] = th
            # th.join()



if __name__ == "__main__":
    w = Watcher(config=None, callback=print)

    w.start()


