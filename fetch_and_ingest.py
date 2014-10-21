#!/usr/bin/env python

import os
import subprocess
import sys

## machine you are SSH into
HOST = 'altiscale'
## this may not be necessary
HDFS_ROOT = ''

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
files = list(fetch_file_list(HDFS_ROOT + 'ClimateuniqueArc0'))
#base name is the last part of the file name (not all the directories the file is stored in)
files = [f for f in files if not os.path.basename(f).startswith('_')]
print files

#sys.exit(0)

# Step 2: for each file, download its contents, and ingest into postgres.
for phile in files:
    print 'Fetching file: ' + phile

    # Stream file contents
    hadoop_proc = subprocess.Popen(
        ['ssh', HOST, 'hadoop fs -cat ' + HDFS_ROOT + phile],
        stdout=subprocess.PIPE)

    cat_proc = subprocess.Popen(
        ['cat', '-v'], stdin=hadoop_proc.stdout
    )

    system.exit(0)
  
    # Ingest into postgres
    postgres_proc = subprocess.Popen(
        ['psql', '-c', 'COPY table_name from stdin'],
        stdin=hadoop_proc.stdout)

    postgres_proc.wait()
    hadoop_proc.wait()
