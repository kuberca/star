#!/usr/bin/env python

# this is used to generate training data for the model
# to predict, the classifier is using semantic based methods
#
# given input line, return the label for the input
# input can be a single line, or combine multiple templates
# this class should have some knowledge base to do the label
# label could come from different ways:
#   1. based on rules, for eg, if input contains 'error' 'failed' and other key words
#   2. from direct user feedback, user mark logs as userful or not, this should be of highest priority
#   3. from other extra contexts, for eg, error logs posted in the github issues may indicate it is more critical
#   4. from source codes?  Some error logged but ignored so of not much value? 
#   5. Any other ways to do the label

from . naive import Naive
from . ground_truth import GroundTruth
from . heuristics import Heuristics
from . labels import Label


class Labeler:
    def __init__(self, datadir: str, naive: bool = False):
        self.naive = naive
        # knowledge base
        self.nv = Naive()
        if not naive:
            self.gt = GroundTruth(datadir)
            self.hu = Heuristics(datadir)

        # ordered list of labelers with higher priority from the begining
        # self.labelers = [self.gt, self.hu, self.nv]


    # given an input template, return the label
    def get_label_for_tpl(self, tpl: str): 
        if self.naive:
            return self.nv.get_label_for_tpl(tpl)

        # ground truth is always the first priority
        label = self.gt.get_label_for_tpl(tpl)
        if label is not None:
            return label

        # hueristics show warning instead of error
        label = self.hu.get_label_for_tpl(tpl)
        if label is not None:
            
            if label != str(Label.Normal):
                # print("get from heristics, got: [{}], normal is [{}]".format(label, str(Label.Normal)))
                return str(Label.Warning)
            else:
                return label
                
        # naive show Alert insted of error
        # print("get from naive")
        return self.nv.get_label_for_tpl(tpl)

    def update_ground_truth(self, truth:dict):
        return self.gt.update_data(truth)



if __name__ == "__main__":
    lbr = Labeler(datadir=".")
    print(lbr.get_label("today is a good day"))
    lbr.update_ground_truth({"today is a good day":"__label_Error"})
    print(lbr.get_label("today is a good day"))