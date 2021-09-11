#!/usr/bin/env python

# class to manage  ground truth
# maintain a cache of all ground truth

import json
import os
from os import path


class FileLabeler:
    def __init__(self, data_file: str) -> None:
        self.data_file = data_file

        if  path.isfile(self.data_file):
            with open(self.data_file, 'r') as fp:
                try:
                    self.data = json.load(fp)
                except:
                    self.data = {} 
        else:
            self.data = {}


    def name(self):
        return "FileLabeler"

    def get_data(self):
        return self.data

    def update_data(self, fbs: dict):
        self.data.update(fbs)
        with open(self.data_file, 'w') as fp:
            json.dump(self.data, fp)

    def get_label_for_tpl(self, tpl: str):
        return self.data.get(tpl)
    
    # return all labels in current data cache
    def get_labels(self):
        return self.data.values

    # take the file generated by parser and prep
    # input file format is "{label} {template}"
    def ingest_data(self, prep_file: str):
        print("ingest_data from file", prep_file)
        if path.isfile(prep_file):
            with open(prep_file) as fp:
                for line in fp:
                    sp = line.strip().split(" ", 1)
                    if len(sp) == 2:
                        self.data[sp[1]] = sp[0]

            with open(self.data_file, 'w') as fw:
                json.dump(self.data, fw)
    
