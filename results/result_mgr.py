#!/usr/bin/env python

"""
save prediction results into a storage backend
waiting for user action, to either accept or reject the prediciton
if reject, then need to pass the result to feedback manager
"""
import json, sys

from results.result import Result, Group
from feedback.fb_mgr import FeedbackMgr
from storage.sqlite import SqliteStore


from sems.grouper import Grouper

class ResultMgr:
    def __init__(self, fbmgr: FeedbackMgr, store = None):
        self.fbmgr = fbmgr
        if store is None:
            store = SqliteStore()
        self.store = store

        # grouper group unresolved results using semantic similarity
        self.model_file = "./model/star.bin"
        self.grouper = Grouper(self.store, self.model_file)

    # add results into storage
    # called by predictor
    # before save to storage, need to do
    # 1. check feedback,
    # 2. dedup
    def add(self, result:Result):
        fb = self.fbmgr.get(result.template_id, result.context_id, result.template)

        # do not save is feedback shows it's not an error
        if fb is not None and not fb.is_error():
            #print("is not error from feedback", result.input)
            return
        

        # check if already exists in storage
        res = self.get_unresolved(result.template_id, result.context_id)
        if res is not None:
            res.count += 1
            res.input = result.input
            res.meta = self.merge_meta(res.meta, result.meta)

            # check if grouper is enabled and if yes, then save to grouper
            if self.grouper is not None and not res.group_id > 0:
                group_id = self.grouper.add_result(res)
                res.group_id = group_id

            self.store.save_unresolved(res)
        else:
            # check if grouper is enabled and if yes, then save to grouper
            if self.grouper is not None:
                group_id = self.grouper.add_result(result)
                result.group_id = group_id

            if fb is not None:
                result.label = fb.label
                result.analysis = fb.analysis
            self.store.save_unresolved(result)



    # save into storage  
    def save_unresolved(self, result: Result):
        print("saving predict result", result)
        self.store.save_unresolved(result)

    def save_resolved(self, result: Result):
        print("saving resolved result", result)
        self.store.save_resolved(result)

    # get all results from storage
    def get_all(self):
        return self.store.get_all()

    # get un resolved results from storage, so user can look at it and take action
    def get_unresolved(self, template_id: int, context_id: str) -> Result:
        print("get unresolved template_id", template_id, context_id)
        return self.store.get_unresolved(template_id, context_id)

    # get all un resolved results from storage, so user can look at it and take action
    def get_all_unresolved(self):
        return self.store.get_unresolved()

    # get un resolved results from storage, so user can look at it and take action
    def get_resolved(self, template_id: int, context_id: str) -> Result:
        print("get resolved template_id", template_id, context_id)
        return self.store.get_resolved(template_id, context_id)

    # get all resolved results from storage, could be used for statictics
    def get_all_resolved(self):
        return self.store.get_all_resolved()

    def get_all_unresolved_groups(self):
        groups = self.store.get_groups_with_results()
        #  get the top 10 frequent words in the templates of each group
        for group in groups:
            group.top_words = self.get_top_words(group)

        return groups

    # get one single group with results
    def get_unresolved_group(self, id: int) -> Group:
        group = self.store.get_group_with_results(id)
        return group

    # resolve group
    def resolve_group(self, group: Group):
        for result in group.results:
            result.label = group.label
            result.analysis = group.analysis
            self.resolve(result)

    # get sim scores between two groups
    def get_group_sim_score(self, group1: Group, group2: Group):
        return self.grouper.get_group_sim_score(group1, group2)

    # if user reject the result, means the prediction that the data is 'error' is wrong
    # need to update this result into user feedback, so later prediction can use it as ground truth
    # so it won't be labelled as 'error' again
    # if user accept the result, should mark the result as accepted
    def resolve(self, result):
        self.fbmgr.save(result)
        self.store.resolve(result)


    def merge_meta(self, old: dict, n : dict) -> dict:

        # if same log appears in multiple pods or containers or files, merge them
        # keys = ["file", "pod", "container"]
        # for key in keys:
        #     vold = old.get(key)
        #     vnew = n.get(key)
        #     if vold is not None and vnew not in vold:
        #         n[key] = vold + "," + vnew
        
        return n


    # get top K frequent words in the templates of each group
    def get_top_words(self, group: Group):
        # get all words in all templates
        words = {}
        for result in group.results:
            tokens = result.template.split()
            for token in tokens:
                if self.skip_word(token):
                    continue
                if token not in words:
                    words[token] = 0
                words[token] += 1

        # get top K frequent words
        return self.get_top_k(words.items(), 10)

    # get top K frequent items from a list of items
    def get_top_k(self, items, k):
        k = min(k, len(items))
        return sorted(items, key=lambda x: x[1], reverse=True)[:k]

    # skip some words
    def skip_word(self, word:str):
        if len(word) < 2 or word == "<DATE>" or word == "<TIME>" or word == "<DATETIME>" or word == "<HEX>" or word == "<IP>" or word == "<*>":
            return True

        if any([char.isdigit() or char == '-' for char in word]):
            return True

        return False