#!/usr/bin/env python

"""
Take offline batch data, process
"""
import threading
import magic
import os
import tarfile, zipfile, gzip
import sys

from . mem_queue import MemQueue

# from config.config import Config

def process_log_with_context(mq: MemQueue, meta: dict, callback):
    while True:
        line, context = mq.get()
        callback(line, meta, context)



class Batcher():
    def __init__(self, config, callback) -> None:
        print("callback is", callback)
        self.callback = callback
        self.threads = {}

    def get_key(self, pod: str, container : str):
        return "%s_%s" % (pod, container)

    def start_in_bg(self, file: str):
        th = threading.Thread(target=self.start, args=(file,))
        th.start()

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
        if fm == "text/plain":
            with open(file, 'r') as f:
                meta={"file":os.path.basename(file)}
                mq = self.create_start_mq(meta)
                self.proc_line_in_file(mq, f, False)

        elif fm == "application/x-tar":
            tar = tarfile.open(file)
            for f in tar: 
                if f.name.endswith(".yaml") or f.name.endswith(".json"):
                    continue
                ft = tar.extractfile(f.name)
                if ft is None:
                    continue
                meta={"file":f.name}

                mq = self.create_start_mq(meta)
                self.proc_line_in_file(mq, ft, True)

        elif fm == "application/zip":
            zip = zipfile.ZipFile(file)
            for zf in zip.namelist():
                if zf.endswith(".yaml") or zf.endswith(".json"):
                    continue
                meta={"file":zf}

                mq = self.create_start_mq(meta)
                self.proc_line_in_file(mq, zip.open(zf), True)

        elif fm == "application/gzip":
            zip = gzip.GzipFile(file)
            meta={"file":zip}

            mq = self.create_start_mq(meta)
            self.proc_line_in_file(mq, zip, True)

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

    def proc_line_in_file(self, mq: MemQueue, file, decode: bool):
        for line in file:
            if decode:
                try: 
                    line = line.decode('utf-8')
                except:
                    pass
            mq.put(line)

    def create_start_mq(self, meta):
        mq = MemQueue()
        th = threading.Thread(target=process_log_with_context, args=(mq, meta, self.callback))
        th.start()
        return mq


if __name__ == "__main__":
    batcher = Batcher(config=None, callback=print)
    args = sys.argv[1:]
    batcher.start(args[0])