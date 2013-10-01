#!/usr/bin/env python

import csv
import sys
import sqlite3
from optparse import OptionParser

sensors = {
    '28-000001b4337c': '1',
    '28-000001b4754f': '2',
    '28-000001b43eba': '3',
}

def process_csv_file(csv, sensor, sql):
    data = [x for x in csv if len(x) == 3]
    data = [('%s%s%s%s-%s%s-%s%s %s' % (d[0], d[1], d[2], d[3], d[4], d[5], d[6], d[7], t), c, sensors[sensor]) for (d, t, c) in data]
    sql.executemany('INSERT INTO temperature VALUES(?, ?, ?)', data)

# Parse all the required arguments
parser = OptionParser()
parser.add_option("-f", "--dbfile", dest="database", help="SQLite database to write to", metavar="FILE", default=None)
parser.add_option("-v", "--verbose", action="store_false", dest="verbose", default=False, help="Be verbose")
(options, args) = parser.parse_args()

# Commandline verification
if options.database is None:
    parser.error('Missing database on commandline')
if len(args) < 1:
    parser.error('Missing CSV files on commandline')

# Open the database
conn = sqlite3.connect(options.database)
c = conn.cursor()

# Import CSV files one by one
for cf in args:
    print('Processing %s' % cf)
    sys.stdout.flush()
    try:
        with open(cf, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            sensor = cf.split('.')[1]
            process_csv_file(csvreader, sensor, c)
            conn.commit()
    except:
        print('%s failed(%s)' % (cf, sys.exc_info()[0]))
