#!/usr/bin/env python

# original is the source input, like a log line
# template/template_id:  parsed result of original
# label: output of predictor
# analysis: root cause analysis, if this error have appeared before and user have provided userful feedback on how to resolve it
# context: context of original, useful to backtrace to where it happened
class Result:
    def __init__(self, 
                input: str,
                template: str,
                template_id: int,
                label: str,
                analysis: str = "NA",
                context: str = "NA",
                count: int = 1) -> None:

        self.input = input
        self.template = template
        self.template_id = template_id
        self.label = label
        self.analysis = analysis
        self.context = context
        self.count = count

    def __str__(self) -> str:
        return "%s %s %s %s %d %d" % (self.label, self.analysis, self.input, self.template, self.template_id, self.count)

    def is_error(self):
        return self.label != "Normal"