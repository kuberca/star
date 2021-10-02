#!/usr/bin/env python

"""
Predictor take model and user feedback, to predict label for the log template
input: log line text
output: label for the log

steps:  preprocess to log template
        check if feedback has it
        if not, use model to predict 
"""
import threading
from results.result import Result

class Predictor:
    def __init__(self, preper, model):
        self.preper = preper
        self.model = model
        self.lock = threading.Lock()

    def predict(self, input: str, context: dict = {}):

        self.lock.acquire()
        id, template = self.preper.process(input)
        self.lock.release()
        
        label = self.model.predict(template, context)
        

        result = Result(input=input, label=label, template=template, template_id=id)

        return result

