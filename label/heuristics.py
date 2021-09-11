#!/usr/bin/env python

# class to manage  ground truth
# maintain a cache of all ground truth

import json
import os
from os import path
from . file_labeler import FileLabeler


class Heuristics(FileLabeler):
    def __init__(self, datadir: str) -> None:
        data_file = path.join(datadir, "hu.data.json")
        ingest_file = path.join(datadir, "hu.data.txt")
        super().__init__(data_file)
        super().ingest_data(ingest_file)

    def name(self):
        return "Heuristics"

    