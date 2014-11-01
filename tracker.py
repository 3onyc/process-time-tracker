from __future__ import print_function
from collections import Counter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import psutil
import signal
import sys
import time

from models import LogEntry, metadata

INTERVAL=10 # Seconds
PREVIOUS_EXES = set()
ENGINE = create_engine('sqlite:///db.sqlite', echo=True)

session = sessionmaker(bind=ENGINE)
metadata.create_all(ENGINE)

def get_processes():
    for proc in psutil.process_iter():
        try:
            proc.exe()
        except psutil.AccessDenied:
            continue

        yield proc

def main():
    while True:
        global PREVIOUS_EXES

        exes = set([proc.exe() for proc in get_processes()])
        sess = session()

        # New
        for exe in exes.difference(PREVIOUS_EXES):
            sess.add(LogEntry(exe, LogEntry.STARTED))

        # Ended
        for exe in PREVIOUS_EXES.difference(exes):
            sess.add(LogEntry(exe, LogEntry.STOPPED))

        PREVIOUS_EXES = exes

        sess.commit()
        time.sleep(INTERVAL)

def on_exit(signum, frame):
    sess = session()
    for exe in PREVIOUS_EXES:
        sess.add(LogEntry(exe, LogEntry.STOPPED))
    sess.commit()
    sys.exit(0)

signal.signal(signal.SIGINT, on_exit)
signal.signal(signal.SIGQUIT, on_exit)
signal.signal(signal.SIGTERM, on_exit)

main()
