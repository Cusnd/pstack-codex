"""Append one sanitized decision-log row. Use one writer per log."""
import argparse
import datetime as dt
import os
from pathlib import Path


def clean(value):
    value = value.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')
    return "'" + value if value.startswith(('=', '+', '-', '@')) else value


def append_row(path, values):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        header = 'ts\tphase\tdecision\twhy\tevidence\tresult\n' if os.fstat(descriptor).st_size == 0 else ''
        data = (header + '\t'.join([stamp, *(clean(value) for value in values)]) + '\n').encode('utf-8')
        while data:
            written = os.write(descriptor, data)
            data = data[written:]
    finally:
        os.close(descriptor)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('logfile', type=Path)
    parser.add_argument('cells', nargs=5, metavar='CELL')
    args = parser.parse_args()
    append_row(args.logfile, args.cells)
