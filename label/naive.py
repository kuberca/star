#!/usr/bin/env python

# Naive labler, just return the label based on keywords

class Naive:
    def name(self):
        return "Naive"

    def get_label_for_tpl(self, tpl: str):
        # ignore the template if it have too many tokens, it's probably a debug message printing out some json data
        # if tpl.count(" ") > 100:
        #     return "Normal"
        tokens = tpl.split()
        if len(tokens) > 80:
            return "Normal"

        tpll = tpl.lower()
        if "error" in tpll or "failed" in tpll:
            if "error <nil>" in tpll or "failed false" in tpll or "failed 0" in tpll or "0 pods failed" in tpll:
                return "Normal"
            return "Error"
        return "Normal"