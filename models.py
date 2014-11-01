from sqlalchemy import Table, MetaData, Column, Integer, Text, Enum, DateTime, Index
from sqlalchemy.orm import mapper
from datetime import datetime

metadata = MetaData()

class LogEntry(object):
    STARTED = 'started'
    STOPPED = 'stopped'

    def __init__(self, exe, entry_type, created_at = None):
        self.exe = exe
        self.entry_type = entry_type
        self.created_at = created_at if created_at is not None else datetime.now()

log_entry = Table('log_entries', metadata,
    Column('id', Integer, primary_key=True),
    Column('exe', Text()),
    Column('entry_type', Enum(LogEntry.STARTED, LogEntry.STOPPED, name='EntryType')),
    Column('created_at', DateTime),

    Index('idx_exe', 'exe'),
    Index('idx_created_at', 'created_at')

)

mapper(LogEntry, log_entry)
