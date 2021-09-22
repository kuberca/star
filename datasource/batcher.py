#!/usr/bin/env python

"""
Take offline batch data, process
"""
import threading
import magic
import os
import tarfile, zipfile, gzip
import sys

# from config.config import Config

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
                for line in f:
                    self.callback(line, meta)

        elif fm == "application/x-tar":
            tar = tarfile.open(file)
            for f in tar: 
                ft = tar.extractfile(f.name)
                meta={"file":f.name}
                for line in ft:
                    self.decode_proc(line, meta)

        elif fm == "application/zip":
            zip = zipfile.ZipFile(file)
            for zf in zip.namelist():
                meta={"file":zf}
                for line in zip.open(zf):
                    self.decode_proc(line, meta)

        elif fm == "application/gzip":
            zip = gzip.GzipFile(file)
            meta={"file":zip}
            for line in zip:
                self.decode_proc(line, meta)

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

    def decode_proc(self, line: str, meta: dict):
        try: 
            linedecode = line.decode('utf-8')
            self.callback(linedecode, meta)
        except:
            pass

if __name__ == "__main__":
    batcher = Batcher(config=None, callback=print)
    args = sys.argv[1:]
    batcher.start(args[0])