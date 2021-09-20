#!/usr/bin/env python

"""
use in memory dict as storage backend 
"""

from results.result import Result


class MemStore:
    def __init__(self) -> None:
        self.unresolved = {}
        self.resolved = {}

    # save into storage  
    def save_unresolved(self, result: Result):
        self.unresolved[result.template_id] = result

    def save_resolved(self, result: Result):
        self.resolved[result.template_id] = result

    # get un resolved results from storage, so user can look at it and take action
    def get_unresolved(self, template_id: int) -> Result:
        return self.unresolved.get(template_id)

    # get all un resolved results from storage, so user can look at it and take action
    def get_all_unresolved(self):
        return self.unresolved.values()

    # get un resolved results from storage, so user can look at it and take action
    def get_resolved(self, template_id: int) -> Result:
        return self.resolved.get(template_id)

    # get all resolved results from storage, could be used for statictics
    def get_all_resolved(self):
        return self.resolved.values()

    # get all results from storage
    def get_all(self):
        return self.get_all_unresolved(), self.get_all_resolved()

    # if user reject the result, means the prediction that the data is 'error' is wrong
    # need to update this result into user feedback, so later prediction can use it as ground truth
    # so it won't be labelled as 'error' again
    # if user accept the result, should mark the result as accepted
    def resolve(self, result):
        self.unresolved.pop(result.template_id)
        self.resolved[result.template_id] = result