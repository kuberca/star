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

from storage.mem import MemStore
from results.result import Result


class FeedbackMgr:
    def __init__(self, remote_url: str, store = None) -> None:
        if store is None:
            print("use memstore for feedback")
            store = MemStore()
        else:
            print("use sqlite for feedback")
        self.store = store

        if not remote_url:
            self.initialize(remote_url)

    # download feedbacks from remote_url and put into local cache
    def initialize(self, remote_url: str):
        print("fake initialize from %s" % (remote_url))

    # take an array of user feedbacks and update local cache
    def save(self, result):
        self.store.save_feedback(result)

    # update changes in local cache to upstream remote_url
    def update_remote(self, remote_url):
        pass

    # get feedback from local cache for the given template
    # if exist, then the feedback is treated as ground truth
    # if not, return None, then predictor need to take further actions
    def get(self, template_id: int) -> Result:
        return self.store.get_feedback(template_id)


