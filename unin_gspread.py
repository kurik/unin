#!/usr/bin/env python

import sqlite3
import optparse
import sys
import uninconfig
import uninlog
from uninlog import log_info, log_err
import httplib2
import oauth2client.client
import gspread
from oauth2client.file import Storage
from oauth2client.tools import run_flow
import uninaggr


OAUTH2_SCOPE = 'https://spreadsheets.google.com/feeds'


# Parse command line
parser = optparse.OptionParser()
parser.add_option("-c", "--cfgfile", dest="cfgfile", help="Config file [%s]" % uninconfig.CONFIG_FILE, metavar = "FILE", default = None)
parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Be verbose on console and do not use syslog.")
(options, args) = parser.parse_args()

# Initialize logging
uninlog.console = options.verbose

# Parse the config file
config = uninconfig.UninConfig()
config.read(options.cfgfile)


###
log_info('Gathering data')
current = uninaggr.get_current()
daily = uninaggr.get_daily()
###

row = 2
log_info('Aggregating data')
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

cells = dict()
for stamp in sorted(daily_merged):
    cells['%s:%s' % (row, 1)] = stamp
    cells['%s:%s' % (row, 2)] = daily_merged[stamp][0]
    cells['%s:%s' % (row, 3)] = daily_merged[stamp][1]
    row += 1

log_info('Authenticating to Google drive')
flow = oauth2client.client.flow_from_clientsecrets(config.get_client_secret(), OAUTH2_SCOPE)
# Try to get credentials from a Store
storage = Storage(config.get_client_storage())
credentials = storage.get()


if credentials is None:
    # Perform OAuth2.0 authorization flow.
    flow.params.update({'access_type':'offline','approval_prompt':'force'})
    flow.redirect_uri = oauth2client.client.OOB_CALLBACK_URN
    authorize_url = flow.step1_get_authorize_url()
    print('Go to the following link in your browser: ' + authorize_url)
    if sys.version_info[0] == 2:
        code = raw_input('Enter verification code: ').strip()
    else:
        code = input('Enter verification code: ').strip()
    credentials = flow.step2_exchange(code)
    storage.put(credentials)
elif credentials.invalid:
    credentials = run_flow(flow, storage)

gc = gspread.authorize(credentials)
try:
    sh = gc.open(config.get_gsheet())
except gspread.httpsession.HTTPError as e:
    log_err('Status: ' + str(e.response.status))
    log_err('Reason:' + str(e.response.reason))

#rows = len(cells) + 10
rows = int((len(cells) / 3) + 100)
log_info('Getting current data from spreadsheet (%s rows)' % rows)
dashboard = sh.worksheet("DAILY")
cell_list = dashboard.range('A2:C%s' % str(rows))
log_info('Reshufling data')
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
