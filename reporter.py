from __future__ import print_function
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import LogEntry, metadata

from collections import defaultdict
from datetime import timedelta
from os.path import basename

import config as cfg

ENGINE = create_engine('sqlite:///db.sqlite', echo=False)

session = sessionmaker(bind=ENGINE)
metadata.create_all(ENGINE)
totals = defaultdict(timedelta)


def get_entry_chunks(query):
    previous_entry = None
    for entry in query.all():
        if previous_entry:
            yield previous_entry, entry

        previous_entry = entry


def main():
    q = session().query(LogEntry).order_by(
        LogEntry.exe,
        LogEntry.created_at
    )

    for first, second in get_entry_chunks(q):
        if first.exe != second.exe:
            continue

        # Due to previous checks 2nd entry should be stopped
        if first.entry_type == LogEntry.STARTED \
           and second.entry_type == LogEntry.STOPPED:
            delta = second.created_at - first.created_at
            totals[first.exe] += delta

    print("{:<40s} {:<6s}".format("Program", "Hours Running"))
    for exe, delta in sorted(totals.items(), key=lambda i: i[1], reverse=True):
        if not whitelisted(exe):
            continue

        total_hours = delta.total_seconds() / 3600
        name = get_name(normalize(exe))

        print("{:<40s} {:<6.2f}".format(name, total_hours))


def normalize(exe):
    return " ".join(exe.split(" ")[get_start_part(exe):])


def get_start_part(exe):
    base_exe = basename(exe.split(" ")[0])
    return cfg.track_parts[base_exe] - 1 if base_exe in cfg.track_parts else 0


def get_name(normalized):
    return cfg.exe_map[normalized] if normalized in cfg.exe_map else normalized


def whitelisted(exe):
    if len(cfg.whitelist) == 0:
        return True

    if exe in cfg.whitelist:
        return True

    if normalize(exe) in cfg.whitelist:
        return True

    for entry in cfg.whitelist:
        if exe.endswith(entry):
            return True

if __name__ == "__main__":
    main()
