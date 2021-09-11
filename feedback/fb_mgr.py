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

class FeedbackMgr:
    def __init__(self) -> None:
        pass

    # download feedbacks from remote_url and put into local cache
    def initialize(self, remote_url: str):
        pass

    # take an array of user feedbacks and update local cache
    def update(self, feedbacks):
        pass

    # update changes in local cache to upstream remote_url
    def update_remote(self, remote_url):
        pass

    # get all feedbacks from local cache
    def get(self):
        pass


