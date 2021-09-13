#!/usr/bin/env python

"""
watch events and crd/status
tailing logs from pods of namespace specified
pre-process the input data to text message
and call callback to process the data
"""

from ..config.config import Config

class Watcher():
    def __init__(self, config: Config, callback: function) -> None:
        pass


    def start(self):
        # from kubernetes import watch
        # w = watch.Watch()
        # for line in w.stream(v1.read_namespaced_pod_log, name=<pod-name>, namespace='<namespace>'):
        #     log.info(line)

