#!/usr/bin/env python

## to run, go to command line with the right directory where you stored the file, then type: ./fetch_and_ingest.py

import os
import subprocess
import sys

## machine you are SSH into
HOST = 'altiscale'
## this may not be necessary
HDFS_ROOT = ''

PSQL_HOST = 'psql -h climatechangedotgovdata.cmu4mm2fobzj.us-west-2.rds.amazonaws.com -U capppuser -d CAPPPDotGovClimateChange'

pswd = 'cappuser'

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

    try:
        # load file contents en masse
        contents = subprocess.check_output(
            ['ssh', HOST, 'hadoop fs -cat ' + HDFS_ROOT + phile])

        # Ingest into postgres
        postgres_proc = subprocess.Popen(
            ['psql', '-h',  'climatechangedotgovdata.cmu4mm2fobzj.us-west-2.rds.amazonaws.com', '-U', 'capppuser', '-d', 'CAPPPDotGovClimateChange','-c', "COPY unique_captures21oct (src, surt, checksum, date, code, title, description, content) FROM stdin WITH DELIMITER E'\1' NULL '';"],
            stdin=subprocess.PIPE)

        postgres_proc.communicate(input=contents)
        result = postgres_proc.wait()
        if result:
            raise Exception("Ingest failure")

# stream results to the consule when you run it -  be able to see the output you've run
  #  cat_proc = subprocess.Popen(
  #      ['cat', '-v'], stdin=hadoop_proc.stdout
  #  )

#    system.exit(0)

    except Exception as e:
        print '### Exception on file %s : %s' % (phile, e)


