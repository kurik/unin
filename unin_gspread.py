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

# Try to get credentials from a Store
storage = Storage(config.get_client_storage())
credentials = storage.get()

if credentials is None:
    # Perform OAuth2.0 authorization flow.
    flow = oauth2client.client.flow_from_clientsecrets(config.get_client_secret(), OAUTH2_SCOPE)
    flow.redirect_uri = oauth2client.client.OOB_CALLBACK_URN
    authorize_url = flow.step1_get_authorize_url()
    print('Go to the following link in your browser: ' + authorize_url)
    try: # The pythov 2.x/3.x compatability
        code = raw_input('Enter verification code: ').strip()
    except:
        code = input('Enter verification code: ').strip()
    credentials = flow.step2_exchange(code)
    storage.put(credentials)
log_info('Authentication to Google drive succeeded.')

gc = gspread.authorize(credentials)
try:
    sh = gc.open(config.get_gsheet())
except gspread.httpsession.HTTPError as e:
    log_err('Status: ' + str(e.response.status))
    log_err('Reason:' + str(e.response.reason))


###
log_info('Aggregating data')
import uninaggr
data = uninaggr.get_current()
stamp = data[config.get_in_sensor()]['stamp'].replace(' ', '\n')
out_current = data[config.get_out_sensor()]['temperature']
in_current = data[config.get_in_sensor()]['temperature']


data = uninaggr.get_aggr(1)
out_24_avg = data[config.get_out_sensor()]["avg"]
out_24_min = data[config.get_out_sensor()]["min"]
out_24_max = data[config.get_out_sensor()]["max"]
in_24_avg = data[config.get_in_sensor()]["avg"]
in_24_min = data[config.get_in_sensor()]["min"]
in_24_max = data[config.get_in_sensor()]["max"]

data = uninaggr.get_aggr(7)
out_w_avg = data[config.get_out_sensor()]["avg"]
out_w_min = data[config.get_out_sensor()]["min"]
out_w_max = data[config.get_out_sensor()]["max"]
in_w_avg = data[config.get_in_sensor()]["avg"]
in_w_min = data[config.get_in_sensor()]["min"]
in_w_max = data[config.get_in_sensor()]["max"]

data = uninaggr.get_aggr(30)
out_m_avg = data[config.get_out_sensor()]["avg"]
out_m_min = data[config.get_out_sensor()]["min"]
out_m_max = data[config.get_out_sensor()]["max"]
in_m_avg = data[config.get_in_sensor()]["avg"]
in_m_min = data[config.get_in_sensor()]["min"]
in_m_max = data[config.get_in_sensor()]["max"]

data = uninaggr.get_aggr(365)
out_y_avg = data[config.get_out_sensor()]["avg"]
out_y_min = data[config.get_out_sensor()]["min"]
out_y_max = data[config.get_out_sensor()]["max"]
in_y_avg = data[config.get_in_sensor()]["avg"]
in_y_min = data[config.get_in_sensor()]["min"]
in_y_max = data[config.get_in_sensor()]["max"]
###

log_info('Saving aggregated data to Google spreadsheet')
dashboard = sh.worksheet("SUMMARY")
cell_list = dashboard.range('A1:I6')
for cell in cell_list:
    if cell.row == 1:
        if cell.col == 1:
            cell.value = stamp
    if cell.row == 2:
        if cell.col == 2:
            cell.value = out_current / 1000.0
        if cell.col == 3:
            cell.value = in_current / 1000.0
    if cell.row == 3:
        if cell.col == 2:
            cell.value = out_24_avg / 1000.0
        if cell.col == 3:
            cell.value = in_24_avg / 1000.0
        if cell.col == 5:
            cell.value = out_24_min / 1000.0
        if cell.col == 6:
            cell.value = in_24_min / 1000.0
        if cell.col == 8:
            cell.value = out_24_max / 1000.0
        if cell.col == 9:
            cell.value = in_24_max / 1000.0
    if cell.row == 4:
        if cell.col == 2:
            cell.value = out_w_avg / 1000.0
        if cell.col == 3:
            cell.value = in_w_avg / 1000.0
        if cell.col == 5:
            cell.value = out_w_min / 1000.0
        if cell.col == 6:
            cell.value = in_w_min / 1000.0
        if cell.col == 8:
            cell.value = out_w_max / 1000.0
        if cell.col == 9:
            cell.value = in_w_max / 1000.0
    if cell.row == 5:
        if cell.col == 2:
            cell.value = out_m_avg / 1000.0
        if cell.col == 3:
            cell.value = in_m_avg / 1000.0
        if cell.col == 5:
            cell.value = out_m_min / 1000.0
        if cell.col == 6:
            cell.value = in_m_min / 1000.0
        if cell.col == 8:
            cell.value = out_m_max / 1000.0
        if cell.col == 9:
            cell.value = in_m_max / 1000.0

    if cell.row == 6:
        if cell.col == 2:
            cell.value = out_y_avg / 1000.0
        if cell.col == 3:
            cell.value = in_y_avg / 1000.0
        if cell.col == 5:
            cell.value = out_y_min / 1000.0
        if cell.col == 6:
            cell.value = in_y_min / 1000.0
        if cell.col == 8:
            cell.value = out_y_max / 1000.0
        if cell.col == 9:
            cell.value = in_y_max / 1000.0

dashboard.update_cells(cell_list)
