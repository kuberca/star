#!/usr/bin/python

import json
import logging
import os
import subprocess
import sys
import time, re
from os import path
from os.path import dirname
import argparse

from .drain3 import TemplateMiner
from .drain3.template_miner_config import TemplateMinerConfig
from .drain3.file_persistence import FilePersistence

import fasttext

class Template:
    def __init__(self, id: int, text:str, size: int):
        self.id = id
        self.text = text
        self.size = size

    def __str__(self) -> str:
        return str(self.id)  + " " + str(self.size) + " " + self.text

class LogParserNLP:
    def __init__(self, model_file: str):
        if not path.isfile(model_file):
            raise Exception(f"Model file {model_file} not found.")

        self.model = fasttext.load_model(model_file)
        self.id_to_template = {}
        self.text_to_template = {}

        self.template_file = "./template_nlp.txt"
        if path.isfile(self.template_file):
            self.load_templates()

    # interface for preper, userd by predictor, input is single line
    def process(self, line: str):
        out = []
        tokens = re.split(r'\\|\s|:|;|,|\*|\"|\'|=|\[|\]|\(|\)|{|}' ,line.strip())
        for token in tokens:
            if token == '<*>':
                out.append(token)
            else:
                label = self.model.predict(token)[0][0]
                if label == '__label__var':
                    out.append("<*>")
                else:
                    out.append(token)
        
        text = " ".join(out)
        if text in self.text_to_template:
            tpl = self.text_to_template[text]
            tpl.size += 1
            return tpl.id, text
        else:
            tpl = Template(len(self.id_to_template), text, 1)
            self.id_to_template[tpl.id] = tpl
            self.text_to_template[text] = tpl
            return tpl.id, text

    # save templates to file
    def save_templates(self):
        with open(self.template_file, "w") as f:
            for tpl in self.id_to_template.values():
                f.write(f"{tpl.id}\t{tpl.text}\t{tpl.size}\n")


    # load templates from file
    def load_templates(self):
        with open(self.template_file, "r") as f:
            for line in f:
                id, text, size = line.strip().split("\t")
                tpl = Template(int(id), text, int(size))
                self.id_to_template[tpl.id] = tpl
                self.text_to_template[tpl.text] = tpl

    # return current templates
    def get_templates(self):
        self.save_templates()
        sorted_templates = sorted(self.id_to_template.values(), key=lambda it: it.size, reverse=True)
        return sorted_templates


