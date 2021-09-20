#!/usr/bin/env python

"""
backend server
initialize all classes (watcher/preper/results/feedback/model)
start watcher
"""
import re

from config.config import Config
from predictor.predict import Predictor
from datasource.watcher import Watcher
from prep.log_parser import LogParser
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
        self.preper = LogParser(config_file=prepcfg["config_file"], persist=True, persist_dir=prepcfg["persist_dir"])
        self.labler = Labeler(naive=True, datadir=prepcfg["persist_dir"])
        self.feedback = FeedbackMgr(remote_url="", store=store)
        self.results = ResultMgr(fbmgr=self.feedback, store=store)

        self.predictor = Predictor(preper=self.preper, model=self.labler)
        self.watcher = Watcher(config=config, callback=self.watch_callback)
    
    
    def start(self):
        self.watcher.start()


    # start in back ground
    def start_in_gb(self):
        self.watcher.start_in_bg()

    def watch_callback(self, line: str):
        text, context = self.split_line(line)

        result = self.predictor.predict(text)
        
        if result.is_error():
            result.context = context
            self.results.add(result)

    def split_line(self, line: str):
        k8s_log = re.compile("(.*) \"msg\"=(.*)")
        m = k8s_log.match(line)
        if m:
            context = m.group(1)
            text = m.group(2)
        else:
            text = line
            context = {}
        return text, context

if __name__ == "__main__":
    cfg = {}
    cfg["drain3"]={"config_file":"drain3.ini", "persist_dir":"."}
    server = Server(config=cfg)
    server.start()

