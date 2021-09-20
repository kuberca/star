#!/usr/bin/env python

# Naive labler, just return the label based on keywords

class Naive:
    def name(self):
        return "Naive"

    def get_label_for_tpl(self, tpl: str):
        tpll = tpl.lower()
        if "error" in tpll or "fail" in tpll:
            return "Error"
        return "Normal"