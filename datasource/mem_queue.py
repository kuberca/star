#!/usr/bin/env python

"""
input lines need to be put into this queue
so that for each line, we can get the before and after lines as context
use the target line together with the contex for prediction
"""
import threading
from queue import Queue

QueueSize = 1024 * 1024

# lines before and after current line as context
ContextLength = 10

# place hoolder for original line
OriginalLine = "<ORIGINAL_LINE>"

class Item:
    def __init__(self, input: str, context: dict = {}) -> None:
        self.input = input
        self.context = context

    def __str__(self) -> str:
        return "input: [%s], context: [%s]" % (self.input, self.context)

class MemQueue:
    def __init__(self, queue_size: int = QueueSize, context_length: int = ContextLength) -> None:
        # for all the input lines
        self.lines_queue = Queue(maxsize=queue_size)
        
        # for generated items for output
        self.item_queue = Queue(maxsize=queue_size)

        # used to get lines before and after current line as context
        # max size should be context_length + 1
        self.contexts = []
        self.context_length = context_length

        self.lock = threading.Lock()

        self.bg_worker()


    def put(self, line: str, context: dict = {}) -> None:
        item = Item(input=line, context=context)
        self.lock.acquire()
        self.lines_queue.put(item)
        self.lock.release()


    def get(self):
        item = self.item_queue.get()
        return item.input, item.context

    
    def bg_worker(self):
        th = threading.Thread(target=self.worker)
        th.start()



    # generate item from lines when there are enough contexts
    def worker(self):
        while True:
            if len(self.contexts) <= self.context_length:
                item = self.lines_queue.get()
                self.contexts.append(item)
                
                continue

            idx = int(self.context_length / 2)
            item = self.contexts[idx]
            lines = []
            for i in range(idx):
                lines.append(self.contexts[i].input)
            lines.append(OriginalLine)
            for i in range(idx+1, self.context_length+1):
                lines.append(self.contexts[i].input)
            item.context = {}
            item.context["lines"] = lines
            self.item_queue.put(item)
            self.contexts = self.contexts[1:]
                
    def test_reader(self):
        while True:
            item = self.get()
            print("item got is", item)

    def test_bg_reader(self):
        th = threading.Thread(target=self.test_reader)
        th.start()

if __name__ == "__main__":
    mq = MemQueue(queue_size=10, context_length=4)
    mq.bg_worker()
    mq.test_bg_reader()

    for i in range(20):
        input = "input number %d" % (i)
        context = {"no": i}
        print("create", i)
        mq.put(line=input)

