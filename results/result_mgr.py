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
from sems.error_type_nlp import ErrorTypeNLP

class ResultMgr:
    def __init__(self, fbmgr: FeedbackMgr, store = None):
        self.fbmgr = fbmgr
        if store is None:
            store = SqliteStore()
        self.store = store

        # grouper group unresolved results using semantic similarity
        self.model_file = "./model/star.bin"
        self.grouper = Grouper(self.store, self.model_file)

        # error_type classifier
        self.error_type_model_file = "./model/error_type_cla.bin"
        self.error_type_model = ErrorTypeNLP(self.error_type_model_file)

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
        

        # check if already exists in unresolved db
        res = self.get_unresolved(result.template_id, result.context_id)
        if res is None:
            # check if exist in resolved db
            res = self.get_resolved(result.template_id, result.context_id)

        if res is not None:
            # result already saved to unresolved db previously
            res.count += 1
            res.input = result.input
            # update template because template will also keep updated when new variables detected
            res.template = result.template
            res.meta = self.merge_meta(res.meta, result.meta)
            res.context = result.context

            # if result not belongs to any group yet,  then save to grouper
            if not res.group_id > 0:
                group_id = self.grouper.add_result(res)
                res.group_id = group_id

            self.store.save_unresolved(res)
        else:
            # first time to save this template into db
            if fb is not None:
                result.label = fb.label
                result.analysis = fb.analysis
                result.error_type = fb.error_type
            
            # if error_type is empty, use classifier to predict
            if result.error_type == "":
                result.error_type = self.error_type_model.predict(result.template)
                print("got error_type from nlp: ", result.error_type)

            # if result not belongs to any group yet,  then save to grouper
            group_id = self.grouper.add_result(result)
            result.group_id = group_id
            print("got error_type from nlp, group id: ", group_id)

            self.store.save_unresolved(result)

    # split result from group, save into another manual group
    # mark both result and group as manual so there is no merge
    def split_result_from_group(self, result: Result):
        if result.group_id == 0:
            return 

        group = self.grouper.split_result_from_group(result)
        result.group_id = group.group_id

        self.save_unresolved(result)   

    # reverse operation of about split_result_from_group
    # set group unmanual to set the manual_group flag to false
    # then do a merge group
    def set_group_unmanual(self, group: Group):
        group.manual_group = False
        self.store.save_group(group)
        self.grouper.merge_groups()

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
        # print("get unresolved template_id", template_id, context_id)
        return self.store.get_unresolved(template_id, context_id)

    # get all un resolved results from storage, so user can look at it and take action
    def get_all_unresolved(self):
        return self.store.get_all_unresolved()

    # get all resolved results from storage, so user can look at it and take action
    def get_all_resolved(self):
        return self.store.get_all_resolved()

    # get un resolved results from storage, so user can look at it and take action
    def get_resolved(self, template_id: int, context_id: str) -> Result:
        print("get resolved template_id", template_id, context_id)
        return self.store.get_resolved(template_id, context_id)

    # get all resolved results from storage, could be used for statictics
    def get_all_resolved(self):
        return self.store.get_all_resolved()

    def get_all_unresolved_groups(self):
        groups = self.store.get_groups_with_results(0)
        return groups

    def get_all_resolved_groups(self):
        groups = self.store.get_groups_with_results(1)
        return groups

    # get one single group with results
    def get_unresolved_group(self, id: int) -> Group:
        return self.store.get_group_with_results(id, resolved=0)

    # get one single group with results
    def get_resolved_group(self, id: int) -> Group:
        return self.store.get_group_with_results(id, resolved=1)

    # resolve all unresolved groups
    def resolve_all(self):
        groups = self.get_all_unresolved_groups()
        for g in groups:
            self.resolve_group(g)

    # resolve group
    def resolve_group(self, group: Group):
        for result in group.results:
            result.label = group.label
            result.analysis = group.analysis
            result.error_type = group.error_type
            self.resolve(result)

        self.store.save_group(group)

    # get sim scores between two groups
    def get_group_sim_score(self, group1: Group, group2: Group):
        return self.grouper.get_group_sim_score(group1, group2)

    # get sim scores between two results
    def get_result_sim_score(self, result1: Result, result2: Result):
        return self.grouper.get_results_sim_score(result1, result2)

    # if user reject the result, means the prediction that the data is 'error' is wrong
    # need to update this result into user feedback, so later prediction can use it as ground truth
    # so it won't be labelled as 'error' again
    # if user accept the result, should mark the result as accepted
    def resolve(self, result):
        self.fbmgr.save(result)
        self.store.resolve(result)

    # get all templates from storage
    def get_all_templates(self):
        templates = self.store.get_all_templates()
        if templates is None:
            return []
            
        self.template_file = "./template_nlp.txt"
        with open(self.template_file, "w") as f:
            for tpl in templates:
                f.write(f"{tpl}\n")
        return templates

    def cleanup(self):
        self.store.cleanup()

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