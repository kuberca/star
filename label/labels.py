#!/usr/bin/env python

# labels

from enum import Enum

class Label(Enum):
    Normal = 0
    Alert = 1
    Warning = 2
    Error = 3

    def __str__(self):
        return "__label__{}".format(self.name)
