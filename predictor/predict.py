#!/usr/bin/env python

"""
Predictor take model and user feedback, to predict label for the log template
input: log line text
output: label for the log

steps:  preprocess to log template
        check if feedback has it
        if not, use model to predict 
"""
import threading, re
from results.result import Result

OriginalLine = "<ORIGINAL_LINE>"

class Predictor:
    def __init__(self, preper, model):
        self.preper = preper
        self.model = model
        self.lock = threading.Lock()

    def predict(self, line: str, meta: dict={}, context: dict = {}) -> Result:
        text, info = self.split_line(line)
        meta.update({"info":info})

        self.lock.acquire()
        id, template = self.preper.process(text)
        self.lock.release()

        context_id, context_template = self.get_context_info(context=context)

        label = self.model.predict(template, context_template)

        result = Result(input=text, label=label, 
            template=template, template_id=id, 
            context_template=context_template, context_id=context_id, 
            meta=meta, context=context)

        return result

    def get_context_info(self, context: dict) :
        return "context_id", "context_template"

        # lines = context.get("lines")
        # if lines is None:
        #     return ""
        # ids = []
        # templates = []
        # for line in lines:
        #     if line == OriginalLine:
        #         continue
        #     text, info = self.split_line(line)
        #     self.lock.acquire()
        #     id, template = self.preper.process(text)
        #     self.lock.release()
        #     ids.append(str(id))
        #     templates.append(template)

        #########################
        # fake context_id here to only use template ID as key
        # remember to revert
        #########################
        #return "-".join(ids), ",".join(templates)
        # return "context_id", ",".join(templates)

    def split_line(self, line: str):
        msg_log = re.compile("(.*) \"?msg\"?=(.*)")
        dot_go_log = re.compile("(.*\.go[: ]\d+[:\]])(.*)")
        m = msg_log.match(line)
        if m:
            info = m.group(1)
            text = m.group(2)
        else:
            m = dot_go_log.match(line)
            if m:
                info = m.group(1)
                text = m.group(2)
            else:
                text = line
                info = {}
        return text, info