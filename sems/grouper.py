#!/usr/bin/env python

"""
grouper groups unresolved results into groups based on semantic similarity.
"""

from typing import List
from results.result import Result

class Grouper:
    def __init__(self) -> None:
        self.sim_score_min = 0.95


    # add a result to the grouper
    # steps:
    # 1. check if the result is already in a group
    # 2. check if the result is similar to any other result in a group
    # 3. if it is similar to any other result in a group, add it to that group
    # 4. if it is not similar to any other result in a group, create a new group
    # 5. add the result to the new group
    def add_result(self, result: Result) -> None:
        if result.group is not None:
            self.update_group(result.group, result)
            return

        for group in self.get_groups():
            sim_score = self.get_sim_score(group, result)
            if sim_score > self.sim_score_min:
                self.update_group(group, result)
                return
        
        group = self.create_group(result)
        return

    def get_groups(self) -> List[List[Result]]:
        pass

    # update group with new result
    def update_group(self, group, result:Result) -> None:
        return

    # create a new group with new result
    def create_group(self, result:Result) -> None:
        return

    # get similarity score between group and result
    def get_sim_score(self, group, result) -> float:
        return 1.0