#!/usr/bin/env python

"""
take and parse config file
start backendServer 
start apiserver
"""


import argparse


from config import config
from api import api
from backend import backend

parser = argparse.ArgumentParser(description='Auto Root Cause Analysis for Developers.')

parser.add_argument('config', metavar='config', type=str, help='configuration file')
args = parser.parse_args()
config_file = args.config

cfg = config.load(config_file)

# start backend server
backendServer = backend.Server(cfg)
backendServer.start()

# start apiserver
apiServer = api.Server(cfg)
apiServer.start()

