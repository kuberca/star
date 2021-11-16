#!/usr/bin/env python

"""
manage user feedbacks
1. initialize from a central feedback knowledge base
2. persist locally Or (cache locally)
3. take user feedbacks, update local cache, update remote central feedbacks

user feedbacks should contain both positive and negative data
Error data: the system predict as normal, but user manually label as error
Normal data:  system predict as error, but user reject the prediction so it should be treated as normal
"""


import csv
import os
from os import path

from storage.mem import MemStore
from results.result import Result


class FeedbackMgr:
    def __init__(self, remote_url: str, local_file: str, store = None) -> None:
        if store is None:
            print("use memstore for feedback")
            store = MemStore()
        else:
            print("use sqlite for feedback")
        self.store = store
        self.data = {}
        self.local_file = local_file
        self.remote_url = remote_url

        self.initialize(remote_url, local_file)

    # download feedbacks from remote_url and put into local cache
    def initialize(self, remote_url: str, local_file: str):
        if  path.isfile(local_file):
            with open(local_file, 'r') as fp:
                csv_reader = csv.DictReader(fp)
                for row in csv_reader:
                    self.data[row['template']] = row['label']


    # take an array of user feedbacks and update local cache
    def save(self, result):
        self.store.save_feedback(result)

        self.data[result.template] = result.label
        
        with open(self.local_file, 'w') as fw:
            writer = csv.writer(fw)
            writer.writerow(['label', 'template'])
            for key, value in self.data.items():
                writer.writerow([value, key])


    # update changes in local cache to upstream remote_url
    def update_remote(self, remote_url):
        pass

    # get feedback from local cache for the given template
    # if exist, then the feedback is treated as ground truth
    # if not, return None, then predictor need to take further actions
    def get(self, template_id: int, context_id: str, template: str) -> Result:
        res = self.store.get_feedback(template_id, context_id)
        if res is not None:
            return res

        label = self.data.get(template)
        if label is None:
            return None
            
        return Result(input="", template=template, template_id=template_id, label=label)


            
