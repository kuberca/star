#!/usr/bin/env python

"""
backend server
initialize all classes (watcher/preper/results/feedback/model)
start watcher
"""

from ..config.config import Config
from ..predictor.predict import Predictor
from ..datasource.watcher import Watcher
from ..prep.log_parser import LogParser
from ..label.labeler import Labeler
from ..feedback.fb_mgr import FeedbackMgr
from ..results.result_mgr import ResultMgr


class Server():
    def __init__(self, config: Config):
        self.config = config

        self.preper = LogParser()
        self.labler = Labeler()
        self.feedback = FeedbackMgr()
        self.results = ResultMgr()

        self.predictor = Predictor(preper=self.preper, model=self.labler, feedback=self.feedback)
        self.watcher = Watcher(config=config, callback=self.watch_callback)
    
    # start in back ground
    def start(self):
        self.watcher.start()

    def watch_callback(self, intput: str):
        result = self.predictor.predict(input)
        if result.is_error():
            self.results.add(results=result)



