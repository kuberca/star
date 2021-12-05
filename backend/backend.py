#!/usr/bin/env python

"""
backend server
initialize all classes (watcher/preper/results/feedback/model)
start watcher
"""
import re, json

import yappi, time, threading


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
        self.labler = Labeler(naive=True, datadir=prepcfg["persist_dir"])
        self.feedback = FeedbackMgr(remote_url="", local_file="./fb.csv", store=store)
        self.results = ResultMgr(fbmgr=self.feedback, store=store)

        self.predictor = Predictor(preper=self.preper, model=self.labler)
        self.watcher = Watcher(config=config, callback=self.process_line)
        self.batcher = Batcher(config=config, callback=self.process_line)
    
    
    def start_watch(self):
        self.watcher.start()

    # start batcher in back ground
    def start_batch_in_bg(self, file: str):
        self.batcher.start_in_bg(file)

    # start batcher in foreground
    def start_batch(self, file: str):
        self.batcher.start(file)

    # start watcher in back ground
    def start_in_bg(self):
        self.watcher.start_in_bg()

    def process_line(self, line: str, meta: dict, context: dict = {}):

        # print("before prediction", meta)

        result = self.predictor.predict(line, meta, context)
        
        # print("after prediction", result.meta)

        if result.is_error():
            self.results.add(result)



if __name__ == "__main__":
    cfg = {}
    cfg["drain3"]={"config_file":"drain3.ini", "persist_dir":".", "model_file":"model/star.cla.bin"}
    server = Server(config=cfg)
    yappi.start()
    server.start_batch("/tmp/2-cp-with-v1213_1.zip")
    time.sleep(30)
    yappi.stop()

    threads = yappi.get_thread_stats()
    for thread in threads:
        print(
            "Function stats for (%s) (%d)" % (thread.name, thread.id)
        )  # it is the Thread.__class__.__name__
        yappi.get_func_stats(ctx_id=thread.id).print_all()
