#!/usr/bin/env python

import argparse
import fasttext

from prep.log_parser import LogParser
from prep.fasttext_prep import FastPrep

parser = argparse.ArgumentParser(description='input log file.')
parser.add_argument('run_mode', metavar='run_mode', type=str, help='running mode, train or test')
parser.add_argument('in_log_file', metavar='in_log_file', type=str, help='in_log_file file')
args = parser.parse_args()
run_mode = args.run_mode
in_log_file = args.in_log_file


# print result of fasttext tests
# https://fasttext.cc/docs/en/python-module.html
def print_results(N, p, r):
    print("N\t" + str(N))
    print("P@{}\t{:.3f}".format(1, p))
    print("R@{}\t{:.3f}".format(1, r))

def print_false_predicts(test_file: str):
    with open(test_file) as tf:
        for line in tf:
            words, labels = model.get_line(line.strip())
            (plabel,), prop = model.predict(" ".join(words))
            if plabel != labels[0]:
                print("truth: ", labels[0], "predict: ", plabel, words)

###############################################################################
###############################################################################
if __name__ == "__main__":
    model_name = "data/k8s-model.ftz"
    preprop = FastPrep()

    # training mode will save a local model file
    if run_mode == "train":
        train_file, test_file, template_file = preprop.pre_process(in_log_file=in_log_file, split=True)
        model = fasttext.train_supervised(train_file)
        model.save_model(model_name)
        print_results(*model.test(test_file))
        print_false_predicts(test_file)

    # test mode will load the previous mode trained from last training, and do the predition
    elif run_mode == "test":
        train_file, test_file, template_file = preprop.pre_process(in_log_file=in_log_file, split=False)
        model = fasttext.load_model(model_name)
        print_results(*model.test(test_file))
        print_false_predicts(test_file)

    # process the file with naive labeler
    # used to generate data for heristics and ground truth labeler
    elif run_mode == "prep":
        train_file, test_file, template_file = preprop.pre_process(in_log_file=in_log_file, split=False, naive_labeler=True)
        print("input file: ", in_log_file)
        print("processed file: ", test_file)
        print("template file: ", template_file)

    

