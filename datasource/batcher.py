#!/usr/bin/env python

"""
Take offline batch data, process
"""
import threading
import magic
import os
import tarfile, zipfile, gzip
import sys, time
import logging

from . mem_queue import MemQueue
from results.result import Result


# from config.config import Config

def process_log_with_context(mq: MemQueue, callback):
    print("Processing log with context", mq)
    while True:
        line, meta, context = mq.get()
        callback(line, meta, context)

logger = logging.getLogger(__name__)

class Batcher():
    def __init__(self, config, callback) -> None:
        print("callback is", callback)
        self.num_threads = 4
        self.callback = callback
        self.threads = {}
        self.mq = MemQueue()
        self.create_start_queue_worker()
        # self.start_print_threads_in_bg()

    def get_key(self, pod: str, container : str):
        return "%s_%s" % (pod, container)

    def start_print_threads_in_bg(self):
        th = threading.Thread(target=self.print_threads, name="print_threads")
        th.start()

    # print out all the running threads for every second
    def print_threads(self):
        while True:
            for thread in threading.enumerate(): 
                print("running thread: ", thread.name)
            time.sleep(3)

    def start_in_bg(self, file: str):
        th = threading.Thread(target=self.start, name="start_in_bg "+file, args=(file,))
        th.start()

    # given a result, extract the log lines before and after it within the log file
    # steps: 1. find the uploaded file and the log file in it
    #        2. find the file format, and extract the file from the uploaded file
    #        3. find the line number of the result
    #        4. read the log file, and extract the lines before and after the result
    #        5. return the lines
    def get_result_detail_contexts(self, result:Result):
        file_uploaded = result.meta.get("file_uploaded")
        if file_uploaded is None:
            return None
        if not os.path.exists(file_uploaded):
            return None

        file_format = result.meta.get("file_format")
        file = result.meta.get("file")
        line_num = result.context.get("line_num")

        if file_format is None or file is None or line_num is None:
            return None

        print("file_format is", file_format, file, line_num)

        if file_format == "text/plain":
            with open(file_uploaded, 'r') as f:
                return self.get_line_contexts(f, line_num)
        elif file_format == "application/x-tar":
            tar = tarfile.open(file_uploaded)
            return self.get_line_contexts(tar.extractfile(file), line_num)
        elif file_format == "application/zip":
            zip = zipfile.ZipFile(file_uploaded)
            return self.get_line_contexts(zip.open(file), line_num)
        elif file_format == "application/gzip":
            zip = gzip.GzipFile(file_uploaded)
            return self.get_line_contexts(zip, line_num)
        else:
            print("unknown file format for file", file_format, file_uploaded)
            return None



    """
    file could be a txt log file
    or a compressed file in zip/tar/tar.gz format
    """
    def start(self, file: str):
        # if file is text/plain, direct
        # if file is tar or targz/tarzip
        # if file is zip/gzip
        fm = self.get_file_format(file)
        if fm is None:
            print("can't read file", file)
            return    

        print("start to process file ", file)

        if fm == "text/plain":
            with open(file, 'r') as f:
                meta={"file_uploaded":file, "file_format":fm, "file":os.path.basename(file)}
                
                self.proc_line_in_file(meta, f, False)

        elif fm == "application/x-tar":
            tar = tarfile.open(file)
            for f in tar: 
                if f.name.endswith(".yaml") or f.name.endswith(".json"):
                    continue
                ft = tar.extractfile(f.name)
                if ft is None:
                    continue

                meta={"file_uploaded":file, "file_format":fm,"file":f.name}
                self.proc_line_in_file(meta, ft, True)

        elif fm == "application/zip":
            zip = zipfile.ZipFile(file)
            for zf in zip.namelist():
                if zf.endswith(".yaml") or zf.endswith(".json"):
                    continue

                meta={"file_uploaded":file, "file_format":fm,"file":zf}
                self.proc_line_in_file(meta, zip.open(zf), True)

        elif fm == "application/gzip":
            zip = gzip.GzipFile(file)
            meta={"file_uploaded":file, "file_format":fm,"file":zip.name}
            self.proc_line_in_file(meta, zip, True)

    def get_file_format(self, file: str): 
        try:
            fm = magic.from_file(file, mime=True)
            if fm.endswith("zip"):
                try: 
                    tar = tarfile.open(file)
                    return "application/x-tar"
                except:
                    return fm
            return fm
        except :
            return None

    def get_line_contexts(self, file, line_num):
        line_num = int(line_num)
        line_num_before = line_num - 100
        line_num_after = line_num + 100
        if line_num_before < 0:
            line_num_before = 0

        lines = []
        current = 0
        for line in file:
            current += 1
            if current < line_num_before:
                continue
            elif current > line_num_after:
                break
            
            if current == line_num:
                lines.append("<==============================================================================>")
                lines.append(line)
                lines.append("<==============================================================================>")
            else:
                lines.append(line)

        return lines

    def proc_line_in_file(self, meta, file, decode: bool):
        line_num = 0
        for line in file:
            line_num += 1
            if decode:
                try: 
                    line = line.decode('utf-8')
                except:
                    pass

            self.mq.put(line, meta, context={"line_num":line_num})


    # start a new thread to read from the queue and process the lines
    def create_start_queue_worker(self): 
        for i in range(self.num_threads):
            th = threading.Thread(target=process_log_with_context, name="process_log_with_context ", args=(self.mq, self.callback))
            th.start()


if __name__ == "__main__":
    batcher = Batcher(config=None, callback=print)
    args = sys.argv[1:]
    batcher.start(args[0])