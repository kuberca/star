#!/usr/bin/env python

"""
Predictor take model and user feedback, to predict label for the log template
input: log line text
output: label for the log

steps:  preprocess to log template
        check if feedback has it
        if not, use model to predict 
"""

class Predictor:
    def __init__(self, preper, model, feedback):
        self.preper = preper
        self.model = model
        self.feedback = feedback

    def predict(self, input: str):
        template = self.preper.process(input)
        out = self.feedback.get(template)
        if out is None:
            out = self.model.predict(template)
        return out

