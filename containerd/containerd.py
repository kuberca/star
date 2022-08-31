#!/usr/bin/env python

"""
backend server
initialize all classes (watcher/preper/results/feedback/model)
start watcher
"""
import re, json

import yappi, time, threading
import datetime

from config.config import Config
from predictor.predict import Predictor
from datasource.watcher import Watcher
from datasource.batcher import Batcher
from prep.log_parser import LogParser
from prep.log_parser_nlp import LogParserNLP
from label.labeler import Labeler
from feedback.fb_mgr import FeedbackMgr
from results.result_mgr import ResultMgr
from results.result import Result
from storage.sqlite import SqliteStore


def is_result_error(result: str):
    return result and result != "__label__Normal"

class Server():
    def __init__(self, config: Config):
        self.config = config
        prepcfg = config["drain3"]

        store = SqliteStore()
        #self.preper = LogParser(config_file=prepcfg["config_file"], persist=True, persist_dir=prepcfg["persist_dir"])
        self.preper = LogParserNLP(model_file=prepcfg["model_file"])
        # self.labler = Labeler(naive=True, datadir=prepcfg["persist_dir"])
        # self.feedback = FeedbackMgr(remote_url="", local_file="./fb.csv", store=store)
        # self.results = ResultMgr(fbmgr=self.feedback, store=store)

        # self.predictor = Predictor(preper=self.preper, model=self.labler)
        # self.watcher = Watcher(config=config, callback=self.process_line)
        # self.batcher = Batcher(config=config, callback=self.process_line)

         # generate regex for the folloing log line to extract time info, level, and msg
        # May 17 14:37:15 tmp-node-e2e-2b2fdc05-cos-89-16108-659-8 containerd[910]: time="2022-05-17T14:37:15.980792512Z" level=debug msg="event forwarded" ns=k8s.io 
        self.containerd_log = re.compile("(.*) time=\"(.*)\" level=(.*) msg=(.*)")

        self.windows = []
        self.window_start = None
        self.count_dict = None
        self.window_size_in_seconds = 10
    
    
    # for each line in containerd log file, do:
    # 1. parse the line to time, level, message
    # 2. skip lines with level=debug
    # 3. use NLP parser to parse the message, get template id and template text
    # 4. count the number of template id in the message, for each 10 second time window
    # 5. save the result to file 
    def process_containerd_log(self, file: str):
        # print("process_containerd_log", file)
        with open(file, "r") as f:
            for line in f:
                time, level, message = self.split_line_to_time_level_text(line)
                if level == "debug" or level == "":
                    continue

                tplId, tpl = self.preper.process(message)             
                self.count_template(time, tplId, tpl)
        
        self.save_count_result(file)
        self.preper.save_templates()


    def count_template(self, time: str, tplId: str, tpl: str):

        if self.start_new_window(time):
            if self.count_dict is not None:
                self.windows.append(self.count_dict)
               
            self.window_start = datetime.datetime.fromisoformat(time)
            self.count_dict = {}     
            self.count_dict["start"] = time      
            self.count_dict[tplId] = 1        
            
        else:
            if tplId in self.count_dict:
                self.count_dict[tplId] += 1
            else:
                self.count_dict[tplId] = 1
        
    def save_count_result(self, file: str):
        if self.count_dict is not None:
            self.windows.append(self.count_dict)
            self.count_dict = None
        
        self.save_windows(file)


    # serialize self.windows as josn and save to file
    def save_windows(self, file: str):
        with open(file + ".result", "w") as f:
            json.dump(self.windows, f)

    # check if it is a new window
    # input time is in format of "2022-05-17T14:37:15"
    # if input time is 10 seconds after the last window start time, it is a new window
    def start_new_window(self, time: str):
        if self.window_start is None:
            return True
        else:
            # parse time to datetime
            t = datetime.datetime.fromisoformat(time)
            if t > self.window_start + datetime.timedelta(seconds=self.window_size_in_seconds):
                return True
            else:
                return False


    def split_line_to_time_level_text(self, line: str):
        try:
            m = self.containerd_log.match(line)
            if m:
                time = m.group(2)
                # time will be in fromat of "2022-05-17T14:37:15.980792512Z", parse it to "2022-05-17T14:37:15"
                time = time[:19]
                level = m.group(3)
                text = m.group(4)
                return time, level, text
            else:
                return "", "", ""
        except Exception as e:
            print(e)
            return "", "", ""



if __name__ == "__main__":
    cfg = {}
    cfg["drain3"]={"config_file":"drain3.ini", "persist_dir":".", "model_file":"model/star.cla.bin"}
    server = Server(config=cfg)
    
    file="/Users/junzhou/code/rca/data/newk8s/1526569103538524160/artifacts/tmp-node-e2e-2b2fdc05-cos-89-16108-659-8/containerd.log"
    server.process_containerd_log(file)