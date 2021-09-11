#!/usr/bin/env python

"""
save prediction results into a storage backend
waiting for user action, to either accept or reject the prediciton
if reject, then need to pass the result to feedback manager
"""

from .. feedback.fb_mgr import FeedbackMgr

from .. storage.configmap import ConfigMapStore

class ResultMgr:
    def __init__(self, fbmgr: FeedbackMgr, store: ConfigMapStore):
        self.fbmgr = fbmgr
        self.store = store
        

    # add results into storage
    # called by predictor
    def add(self, results):
        pass

    # get all results from storage
    def get_all(self):
        pass

    # get all un resolved results from storage, so user can look at it and take action
    def get_unresolved(self):
        pass

    # get all resolved results from storage, could be used for statictics
    def get_resolved(self):
        pass

    # if user reject the result, means the prediction that the data is 'error' is wrong
    # need to update this result into user feedback, so later prediction can use it as ground truth
    # so it won't be labelled as 'error' again
    # if user accept the result, should mark the result as accepted
    def resolve(self, results):
        pass


