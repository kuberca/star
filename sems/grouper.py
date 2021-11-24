#!/usr/bin/env python

"""
grouper groups unresolved results into groups based on semantic similarity.
"""
import numpy as np

from typing import List
from results.result import Result, Group
from sems.vector import Vector
from storage.sqlite import SqliteStore

class Grouper:
    def __init__(self, store, model_file) -> None:
        if store is None:
            store = SqliteStore()
        self.store = store
        self.sim_score_min = 0.94
        self.group_merge_threshold = 0.96
        self.vector = Vector(model_file)


    # if use strict group sim, then need to check if the result is similar to all results in the group
    # if not, then need to check if the result is similar to the vector of the group which is averaged of results vector
    def strict_group_sim(self) -> bool:
        return True

    # add a result to the grouper, return group_id
    # steps:
    # 1. check if the result is already in a group
    # 2. check if the result is similar to any other result in a group
    # 3. if it is similar to any other result in a group, add it to that group
    # 4. if it is not similar to any other result in a group, create a new group
    # 5. add the result to the new group
    def add_result(self, result: Result) -> int:
        # merge groups if necessary


        # self.merge_groups()

        # if result.group_id > 0:
        #     self.update_group(result.group, result)
        #     return result.group_id

        if self.strict_group_sim():
            groups = self.store.get_groups_with_results()
            for group in groups:
                all_sim = True
                for gr in group.results:
                    sim_score = self.get_results_sim_score(gr, result)
                    if sim_score < self.sim_score_min:
                        all_sim = False
                        break
                if all_sim:
                    result.group_id = group.group_id
                    self.update_group(group, result)
                    return group.group_id

        else:
            for group in self.get_groups():
                sim_score = self.get_sim_score(group, result)
                if sim_score > self.sim_score_min:
                    self.update_group(group, result)
                    return group.group_id
        
        group = self.create_group(result)
        return group.group_id


    def get_group(self, group_id: int) -> Group:
        return self.store.get_group(group_id=group_id)

    def get_groups(self) -> List[Group]:
        return self.store.get_groups()

    # update group with new result
    # average the group's semantic vector with the new result ? 
    def update_group(self, group:Group, result:Result) -> Group:
        print("updating group: " + str(group.group_id))
        g_e = self.get_group(group_id=group.group_id)
        vector = self.get_result_vector(result)
        g_e.vector = (np.array(g_e.vector)*g_e.count + vector) / (g_e.count + 1)
        g_e.count += 1
        return self.store.save_group(g_e)

    # create a new group with new result
    def create_group(self, result:Result) -> Group:
        vector = self.get_result_vector(result)
        group = Group(group_id=0,vector=vector)
        return self.store.save_group(group)

    # get similarity score between group and result
    def get_sim_score(self, group:Group, result:Result) -> float:
        vec = self.get_result_vector(result)
        return self.vector.similarity(group.vector, vec)

    # get similarity score between two results
    def get_results_sim_score(self, result1:Result, result2:Result) -> float:
        vec1 = self.get_result_vector(result1)
        vec2 = self.get_result_vector(result2)
        return self.vector.similarity(vec1, vec2)

    # get similarity score between two groups
    def get_group_sim_score(self, group1:Group, group2:Group) -> float:
        return self.vector.similarity(group1.vector, group2.vector)

    # get semantic vector of the log template
    def get_result_vector(self, result: Result):
        return self.vector.generate(result.template)

    # get all groups, merge two groups if their similarity is above threshold
    def merge_groups(self):
        groups = self.get_groups()
        for i in range(len(groups)):
            for j in range(i+1, len(groups)):
                sim_score = self.get_group_sim_score(groups[i], groups[j])
                if sim_score > self.group_merge_threshold:
                    self.merge_group(groups[i], groups[j])

    # merge two groups
    def merge_group(self, group1: Group, group2: Group):
        print("merging groups: " + str(group1.group_id) + " and " + str(group2.group_id))
        g1_e = self.get_group(group1.group_id)
        g2_e = self.get_group(group2.group_id)
        g1_e.vector = (np.array(g1_e.vector)*g1_e.count + np.array(g2_e.vector)*g2_e.count) / (g1_e.count + g2_e.count)
        g1_e.count += g2_e.count
        self.store.save_group(g1_e)
        self.store.change_group(group2.group_id, group1.group_id)