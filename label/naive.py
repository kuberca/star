#!/usr/bin/env python

# Naive labler, just return the label based on keywords

class Naive:
    def name(self):
        return "Naive"

    def get_label_for_tpl(self, tpl: str):
        tpll = tpl.lower()
        if "error" in tpll or "failed" in tpll:
            if "error <nil>" in tpll or "failed false" in tpll or "failed <*>" in tpll or "0 pods failed" in tpll:
                return "Normal"
            return "Error"
        return "Normal"