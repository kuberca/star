#!/usr/bin/env python

# original is the source input, like a log line
# template/template_id:  parsed result of original
# label: output of predictor
# analysis: root cause analysis, if this error have appeared before and user have provided userful feedback on how to resolve it
# meta: meta info of the log line, useful to backtrace to where it happened
# context: context info of the log line, useful to deep analysis, examples could include: 
#   N lines before and after the log line
#   useful events at time of log happened
#   useful k8s data for related objects at time of log 
#   and others? 
# context_id: aggregated id to represent the context info, used to retrieve same context
# group_id: grouping multiple results into one group with semantic similarity
from typing import List


class Result:
    def __init__(self, 
                input: str,
                template: str,
                template_id: int,
                label: str,
                context_id: str = "",
                context_template: str ="",
                group_id: int = -1,
                analysis: str = "NA",
                meta: dict = {}, 
                context: dict = {},
                count: int = 1,
                error_type: str = "",
                resolved: bool = False) -> None:

        self.input = input
        self.template = template
        self.template_id = template_id
        self.label = label
        self.analysis = analysis
        self.meta = meta
        self.context = context
        self.context_id = context_id
        self.context_template = context_template
        self.group_id = group_id
        # group created by user from remove result from exisitng group
        self.manual_group = False
        self.count = count
        self.error_type = error_type
        self.resolved = resolved

    def __str__(self) -> str:
        return "%s %s %s %s %d %d" % (self.label, self.analysis, self.input, self.template, self.template_id, self.count)

    def is_error(self):
        return self.label != "Normal"


class Group:
    def __init__(self, group_id: int, vector: list = None, manual_group:bool=False, label:str="", 
                error_type:str="", objects:str="", analysis:str="", 
                vector_str: str = "", count: int=1, results: List[Result] = None) -> None:
        self.group_id = group_id
        self.count = count
        self.results = results
        self.top_words = []
        self.analysis = analysis
        self.label = label
        # if manual_group is True, this group is created by user, so do not try to merge with other groups
        self.manual_group = manual_group
        self.error_type = error_type
        # objects is the predicted target object that this group is talking about
        self.objects = objects

        if vector is not None:
            self.vector = vector
        elif  vector_str:
            self.vector = list(map(float, vector_str.strip().split()))
        else:
            raise TypeError("vector should be list or str, given: {}, {}, {}".format(group_id, vector, vector_str))

    def vector_str(self) -> str:
        return " ".join(map(str, self.vector))
