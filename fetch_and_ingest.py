#!/usr/bin/env python

import subprocess
import sys

HOST = 'dbserver01.cs.washington.edu'
HDFS_ROOT = 'hdfs://vega.cs.washington.edu/'

def execute_remote(cmd):
    return subprocess.check_output(['ssh', HOST, cmd])

def fetch_file_list(root):
    s = execute_remote('hadoop fs -lsr ' + root)
    lines = s.split('\n')

    for line in lines:
        toks = line.split()
        if len(toks) == 8:
            yield toks[7]

# Step 1: Fetch list of files
files = list(fetch_file_list(HDFS_ROOT + '/whitaker/outputF'))

# Step 2: for each file, download its contents, and ingest into postgres.
for phile in files:
    print 'Fetching file: ' + phile

    # Stream file contents
    hadoop_proc = subprocess.Popen(
        ['ssh', HOST, 'hadoop fs -cat ' + HDFS_ROOT + phile],
        stdout=subprocess.PIPE)

    # Ingest into postgres
    postgres_proc = subprocess.Popen(
        ['psql', '-c', 'COPY table_name from stdin'],
        stdin=hadoop_proc.stdout)

    postgres_proc.wait()
    hadoop_proc.wait()

