#!/usr/bin/env python
import fasttext
import argparse
from scipy import spatial
import os
import numpy as np
from sklearn.cluster import OPTICS

parser = argparse.ArgumentParser(description='tpl file.')
parser.add_argument('-tpl_file', type=str, help='tpl_file file', default="alllog/templates.txt.vec")
parser.add_argument('-model_file', type=str, help='model_file file', default="alllog/templates.txt.vec")
args = parser.parse_args()
tpl_file = args.tpl_file
model_file = args.model_file
basedir = os.path.dirname(tpl_file)

outs = []

model = fasttext.load_model(model_file)

with open(tpl_file) as f:
    for line in f:
        out = []
        tokens = line.strip().split()
        for token in tokens:
            if token == '<*>':
                out.append(token)
            else:
                label = model.predict(token)[0][0]
                if label == '__label__var':
                    out.append("<*>")
                else:
                    out.append(token)
        outs.append(" ".join(out))



with open(tpl_file+".out", "w") as f:
    for line in outs:
        f.write(line+"\n")
