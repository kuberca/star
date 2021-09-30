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
class Result:
    def __init__(self, 
                input: str,
                template: str,
                template_id: int,
                label: str,
                analysis: str = "NA",
                meta: dict = {}, 
                context: dict = {},
                count: int = 1) -> None:

        self.input = input
        self.template = template
        self.template_id = template_id
        self.label = label
        self.analysis = analysis
        self.meta = meta
        self.context = context
        self.count = count

    def __str__(self) -> str:
        return "%s %s %s %s %d %d" % (self.label, self.analysis, self.input, self.template, self.template_id, self.count)

    def is_error(self):
        return self.label != "Normal"