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


import fasttext



class ErrorTypeNLP:
    def __init__(self, model_file: str):
        if not path.isfile(model_file):
            raise Exception(f"Model file {model_file} not found.")
        else:
            print("loading model file for ErrorTypeNLP: ", model_file)

        self.model = fasttext.load_model(model_file)

    # interface for preper, userd by predictor, input is single line
    def predict(self, line: str):
        label = self.model.predict(line)
        return label[0][0].lstrip('__label__')


