#!/usr/bin/env python

"""
save prediction results into a storage backend
waiting for user action, to either accept or reject the prediciton
if reject, then need to pass the result to feedback manager
"""
from results.result import Result
from feedback.fb_mgr import FeedbackMgr

from storage.file import FileStore

class ResultMgr:
    def __init__(self, fbmgr: FeedbackMgr, store: FileStore):
        self.fbmgr = fbmgr
        self.store = store

        self.resolved={}
        self.unresolved={}


    # add results into storage
    # called by predictor
    # before save to storage, need to do
    # 1. check feedback,
    # 2. dedup
    def add(self, result:Result):
        fb = self.fbmgr.get(result.template_id)

        # do not save is feedback shows it's not an error
        if fb is not None and not fb.is_error():
            return
        
        # check if already exists in storage
        res = self.get_unresolved(result.template_id)
        if res is not None:
            res.count += 1
            res.input = result.input
            self.save(res)
        else:
            if fb is not None:
                result.label = fb.label
                result.analysis = fb.analysis
            self.save(result)

    # save into storage  
    def save(self, result: Result):
        print("saving predict result", result)
        self.unresolved[result.template_id] = result

    # get all results from storage
    def get_all(self):
        pass

    # get all un resolved results from storage, so user can look at it and take action
    def get_unresolved(self, template_id: int) -> Result:
        return self.unresolved.get(template_id)

    # get all resolved results from storage, could be used for statictics
    def get_resolved(self):
        pass

    # if user reject the result, means the prediction that the data is 'error' is wrong
    # need to update this result into user feedback, so later prediction can use it as ground truth
    # so it won't be labelled as 'error' again
    # if user accept the result, should mark the result as accepted
    def resolve(self, results):
        pass


