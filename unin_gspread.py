#!/usr/bin/env python

import gflags
import sqlite3
import optparse
import sys
import uninconfig
import uninlog
import uninaggr
from uninlog import log_info, log_err
import httplib2
from oauth2client.file import Storage
from oauth2client import tools
from oauth2client.client import OAuth2WebServerFlow
import gspread


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

GOOGLE_API_CLIENT_ID = '716515596536-tov4vvgh08l2fvas7esg4hia72s2ue08.apps.googleusercontent.com'
GOOGLE_API_CLIENT_SECRET = 'v5KdTFYehsMrcHQsYgNJWYkP'


flow = OAuth2WebServerFlow(client_id=GOOGLE_API_CLIENT_ID, client_secret=GOOGLE_API_CLIENT_SECRET, scope=OAUTH2_SCOPE, user_agent='Unin-Temperature', access_type='offline', approval_prompt='force')
storage = Storage(config.get_client_storage())
credentials = storage.get()
if credentials is None or credentials.invalid == True:
  credentials =  tools.run(flow, storage)
  storage.put(credentials)

###http = httplib2.Http()
###http = credentials.authorize(http)


###flow = oauth2client.client.flow_from_clientsecrets(config.get_client_secret(), OAUTH2_SCOPE)
# Try to get credentials from a Store
###storage = Storage(config.get_client_storage())
###credentials = storage.get()


###if credentials is None:
    # Perform OAuth2.0 authorization flow.
    ###flow.params.update({'access_type':'offline','approval_prompt':'force'})
    ###flow.redirect_uri = oauth2client.client.OOB_CALLBACK_URN
    ###authorize_url = flow.step1_get_authorize_url()
    ###print('Go to the following link in your browser: ' + authorize_url)
    ###if sys.version_info[0] == 2:
        ###code = raw_input('Enter verification code: ').strip()
    ###else:
        ###code = input('Enter verification code: ').strip()
    ###credentials = flow.step2_exchange(code)
    ###storage.put(credentials)
###elif credentials.invalid:
    ###credentials = run_flow(flow, storage)

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
