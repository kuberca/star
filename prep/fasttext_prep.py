#!/usr/env/python

from . log_parser import LogParser
from label.labeler import Labeler

# input: raw log file
# output: files with format for fasttext:  label template

class FastPrep:
    # input: raw log file
    # input: split, if true, then data will be split into train file and test files
    #               if false, all data will be in test file
    # output: training and testing files contains label to templates
    #         template file contains all templates
    def pre_process(self, in_log_file: str, split: bool, naive_labeler: bool=False):

        # context_len: use how many log line as one training sample
        context_len=1

        # test data ratio = 1/test_mod
        test_mod = 10

        # log parser to parse the log file
        lp = LogParser(persist=True)
        templates, ids = lp.parse_file(in_log_file)

        # labeler to get label for each template
        # naive is used to generate heuristics labels data, will not use ground truth
        # during training/test should not use naive, with will use multiple labelers
        labeler = Labeler(datadir="/Users/junzhou/code/rca/star/data", naive=naive_labeler)

        train_file = in_log_file + ".train.txt"
        test_file = in_log_file + ".test.txt"
        template_file = in_log_file + ".tpl.txt"

        line_cnt = 0

        # template file also the same format: label template
        with open(template_file, "w") as fw:
            for id, tpl in templates.items():
                tpl_str = tpl.get_template()
                label = labeler.get_label_for_tpl(tpl_str)
                fw.write("{} {}\n".format(label, tpl_str))

        print("finish output template file")
        ftrain = open(train_file, 'w')
        ftest = open(test_file, 'w')

        for i in range(len(ids)-context_len+1):
            tmps = []
            for j in range(i, i+context_len):
                if ids[j] not in templates:
                    print("id not in templates", ids[j])
                    continue
                # tokens = templates[ids[j]].log_template_tokens
                # if len(tokens) > 30:
                #     tmps.append((" ".join(tokens[:30])))
                # else:
                #     tmps.append((" ".join(tokens)))
                tmps.append(templates[ids[j]].get_template())

            
            tmpline = "; ".join(tmps)
            label = labeler.get_label_for_tpl(tmpline)
            line_cnt += 1
            if split and line_cnt % test_mod != 0:
                ftrain.write(label + " " + tmpline + "\n")
            else:
                ftest.write(label + " " + tmpline + "\n")

        print("finish output train/test file")
        return train_file, test_file, template_file

if __name__ == "__main__":
    fp = FastPrep()
    file = "/Users/junzhou/code/rca/star/data/github/all.log"
    train_file, test_file, template_file = fp.pre_process(file, split=False)