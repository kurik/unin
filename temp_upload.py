#!/usr/bin/env python3

import sqlite3
import sys
import uninconfig
import uninlog
import uninaggr
from uninlog import log_info, log_err
import httplib2
from oauth2client.file import Storage
from oauth2client import tools
import oauth2client
from apiclient import discovery
import gspread
import argparse
import os


OAUTH2_SCOPE = 'https://spreadsheets.google.com/feeds'

def gauth(oauth2json, oauth2storage, flags = None):
    store = Storage(oauth2storage)
    creds = store.get()
    if creds is None or creds.invalid:
        flow = oauth2client.client.flow_from_clientsecrets(oauth2json, OAUTH2_SCOPE)
        creds = oauth2client.tools.run_flow(flow, store, flags.parse_args())
        store.put(creds)
    return creds

# Parse command line
parser = argparse.ArgumentParser(parents=[tools.argparser], add_help=False)
parser.add_argument("-c", "--cfgfile", dest="cfgfile", help="Config file [%s]" % uninconfig.CONFIG_FILE, metavar = "FILE", default = None)
parser.add_argument("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Be verbose on console and do not use syslog.")
cmdline = parser.parse_args()

oauth2json = os.path.expanduser('~/.temp_upload.json')
oauth2storage = os.path.expanduser('~/.temp_upload')
credentials = gauth(oauth2json = oauth2json, oauth2storage = oauth2storage, flags = parser)

# Initialize logging
uninlog.console = cmdline.verbose

# Parse the config file
config = uninconfig.UninConfig()
config.read(cmdline.cfgfile)


log_info('Gathering and aggregating data')
current = uninaggr.get_current()
daily = uninaggr.get_daily()
daily_merged = dict()
for r in daily:
    (stamp, sensor) = r.split('.')
    if stamp not in daily_merged:
        daily_merged[stamp] = ["", ""]
    if sensor == config.get_out_sensor():
        daily_merged[stamp][0] = daily[r]['temperature']
    elif sensor == config.get_in_sensor():
        daily_merged[stamp][1] = daily[r]['temperature']
    else:
        # Unknow sensor
        continue

row = 2
cells = dict()
for stamp in sorted(daily_merged, reverse=True):
    cells['%s:%s' % (row, 1)] = stamp
    cells['%s:%s' % (row, 2)] = daily_merged[stamp][0]
    cells['%s:%s' % (row, 3)] = daily_merged[stamp][1]
    row += 1

log_info('Authenticating to Google drive')

gc = gspread.authorize(credentials)
sh = None
try:
    sh = gc.open(config.get_gsheet())
except gspread.httpsession.HTTPError as e:
    log_err('Status: ' + str(e.response.status))
    log_err('Reason:' + str(e.response.reason))

log_info('Getting current data from spreadsheet')
try:
    dashboard = sh.worksheet("DAILY")
except:
    credentials =  tools.run(flow, storage)
    storage.put(credentials)
    gc = gspread.authorize(credentials)
    sh = gc.open(config.get_gsheet())
    dashboard = sh.worksheet("DAILY")

rows = int(dashboard.acell('D2').value)
if rows < len(cells):
    rows = len(cells) + 1
cell_list = dashboard.range('A2:C%s' % str(rows))
log_info('Reshuffling data')
for c in cell_list:
    try:
        if c.col == 1:
            c.value = cells['%s:%s' % (c.row, c.col)]
        else:
            c.value = int(cells['%s:%s' % (c.row, c.col)]) / 1000.0
    except:
        c.value = ""
    
log_info('Saving aggregated data to spreadsheet')
dashboard.update_cells(cell_list)
