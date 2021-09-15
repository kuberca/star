#!/usr/bin/python

import json
import logging
import os
import subprocess
import sys
import time
from os import path
from os.path import dirname
import argparse

from prep.drain3 import TemplateMiner
from prep.drain3.template_miner_config import TemplateMinerConfig
from prep.drain3.file_persistence import FilePersistence

def var_has_digit(token: str):
    return any(i == '/' or i == '-' or i.isdigit() for i in token)

class LogParser:
    def __init__(self, config_file: str = "", persist: bool = False, persist_dir: str = "./data"):
        if not path.isfile(config_file):
            config_file = dirname(__file__) + "/drain3.ini"
        print(config_file)

        config = TemplateMinerConfig()
        config.load(config_file)
        config.profiling_enabled = False
        
        if persist:
            persistence = FilePersistence(path.join(persist_dir, "drain3_state.bin"))

        self.template_miner = TemplateMiner(config=config, is_token_variable=var_has_digit, persistence_handler=persistence)

        self.line_count = 0
        self.log_ids = []

        self.logger = logging.getLogger(__name__)
        logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(message)s')

    # interface for preper, userd by predictor, input is single line
    def process(self, line: str):
        result = self.parse_line(line)
        return result["cluster_id"], result["template_mined"]

    # parse_file parse a given file
    # return: 
    #   templates:   template clusters
    #   log_ids:     list of tempalte id of each of the log lines
    def parse_file(self, file: str):
        with open(file) as f:
            lines = f.readlines()

        start_time = time.time()
        batch_start_time = start_time
        batch_size = 10000

        for line in lines:
            line = line.strip()
            result = self.template_miner.add_log_message(line)
            self.log_ids.append(result["cluster_id"])
            self.line_count += 1

            if self.line_count % batch_size == 0:
                time_took = time.time() - batch_start_time
                rate = batch_size / time_took
                self.logger.info(f"Processing line: {self.line_count}, rate {rate:.1f} lines/sec, {len(self.template_miner.drain.clusters)} clusters so far.")
                batch_start_time = time.time()
    
        self.template_miner.save_state("finished")
        
        return self.template_miner.drain.id_to_cluster, self.log_ids


    # parse a single log line
    def parse_line(self, line: str):
        result = self.template_miner.add_log_message(line)
        return result



    # return current templates
    def get_templates(self):
        return self.template_miner.drain.clusters

    # return stats includes how many templates, how many lines parsed etc
    def get_stats(self):
        return self.line_count

    # reset cleanup cached data but keep the templates
    def reset(self):
        self.line_count = 0
        self.log_ids = []

