#!/usr/bin/env python

"""
grouper groups unresolved results into groups based on semantic similarity.
"""

from typing import List
from results.result import Result, Group
from sems.vector import Vector
from storage.sqlite import SqliteStore

class Grouper:
    def __init__(self, store, model_file) -> None:
        if store is None:
            store = SqliteStore()
        self.store = store
        self.sim_score_min = 0.95
        self.vector = Vector(model_file)


    # add a result to the grouper, return group_id
    # steps:
    # 1. check if the result is already in a group
    # 2. check if the result is similar to any other result in a group
    # 3. if it is similar to any other result in a group, add it to that group
    # 4. if it is not similar to any other result in a group, create a new group
    # 5. add the result to the new group
    def add_result(self, result: Result) -> int:
        if result.group_id > 0:
            self.update_group(result.group, result)
            return result.group_id

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
        g_e = self.get_group(group_id=group.group_id)
        vector = self.get_result_vector(result)
        g_e.vector = ([v * g_e.count for v in g_e.vector] + vector) / (g_e.count + 1)
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

    # get semantic vector of the log template
    def get_result_vector(self, result: Result):
        return self.vector.generate(result.template)