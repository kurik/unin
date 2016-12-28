#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import oauth2client.client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient import discovery
import httplib2
import logging
import argparse
import sqlite3
import sys
import os

OAUTH2_SCOPE = 'https://www.googleapis.com/auth/spreadsheets'

# A helper formater for argpartse
class SmartFormatter(argparse.HelpFormatter):
    def _split_lines(self, text, width):
        if text.startswith('R|'):
            return text[2:].splitlines()  
        # this is the RawTextHelpFormatter._split_lines
        return argparse.HelpFormatter._split_lines(self, text, width)

# Parse command line
parser = argparse.ArgumentParser(parents = [tools.argparser], add_help = True, formatter_class = SmartFormatter)
group = parser.add_mutually_exclusive_group()
group.add_argument("-v", "--verbose", dest = "verbose", action = 'count', default = 0,
    help = "Be verbose. More -v parameters ensures more verbosity.")
group.add_argument("-q", "--quiet", dest = "verbose", action = 'store_const', const = -1, help = "Be quiet. Print only Errors.")
parser.add_argument("-l", "--log", "--logfile", dest = "logfile", metavar = "FILE", default = "-",
    help = "R|File to log to instead of logging into the stdout.\nTwo characters have a special meaning:\n"
            "':' - log to syslog\n"
            "'-' - log to stdout")
parser.add_argument("-i", "--identity", "--credentials", dest = "credentials", metavar = "FILE", default = '~/.temp_upload.json',
    required = False, help = "JSON file containing the Google Account credentials.")
parser.add_argument("-s", "--store", "--storefile", dest = "store", metavar = "FILE", default = '~/.temp_upload',
    required = False, help = "File to store Google Auth info.")
parser.add_argument("-d", "--docid", dest = "docid", metavar = "STRING", default = None,
    required = True, help = "ID of the spreadsheet to report to.")
parser.add_argument("-b", "--database", dest = "database", metavar = "FILE", default = '~/var/unin_temperature.db',
    help = "Database file containing the measured values.")
parser.add_argument("sensors", default = None, metavar='N', nargs='+',
    help = "List of sensors ID")

cmdline = parser.parse_args()

# Set the required level of logging
if cmdline.verbose < 0:
    loglevel = logging.ERROR
elif cmdline.verbose == 0:
    loglevel = logging.WARNING
elif cmdline.verbose == 1:
    loglevel = logging.INFO
else:
    loglevel = logging.DEBUG

# Logging into a file
format = '%(asctime)s %(message)s'
if cmdline.logfile == "-":
    logging.basicConfig(level = loglevel, format = format)
elif cmdline.logfile == ":":
    pass
else:
    logging.basicConfig(filename = cmdline.logfile, level = loglevel, format = format)

# Handle google library mess
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

class GAuth(object):
    def __init__(self, oauth2json = None, oauth2storage = None, scope = OAUTH2_SCOPE):
        self.oauth2json = oauth2json
        self.oauth2storage = oauth2storage
        self.scope = scope
        self.store = None
        self.creds = None
        self.service = None
        logging.debug('GAuth object created')

    def auth(self, oauth2json = None, oauth2storage = None, scope = None):
        if oauth2json is not None:
            self.oauth2json = oauth2json
        if oauth2storage is not None:
            self.oauth2storage = oauth2storage
        if scope is not None:
            self.scope = scope
        if self.oauth2json is None:
            raise ValueError('Attribute oauth2json needs to be defined')
        if self.oauth2storage is None:
            raise ValueError('Attribute oauth2storage needs to be defined')
        if self.scope is None:
            raise ValueError('Attribute scope needs to be defined')

        logging.debug('Authenticating to Google, using json(%s) and store(%s)' % (self.oauth2json, self.oauth2storage))
        self.store = Storage(self.oauth2storage)
        self.creds = self.store.get()
        if self.creds is None or self.creds.invalid:
            flow = oauth2client.client.flow_from_clientsecrets(self.oauth2json, self.scope)
            self.creds = oauth2client.tools.run_flow(flow, self.store, parser.parse_args())
            self.store.put(self.creds)
        if 'spreadsheets' in self.scope.lower():
            logging.debug('Authenticating as sheets')
            discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
            self.service = discovery.build('sheets', 'v4', http = self.creds.authorize(httplib2.Http()),
                discoveryServiceUrl = discoveryUrl)
        else:
            logging.debug('Authenticating as drive')
            self.service = discovery.build('drive', 'v3', http = self.creds.authorize(httplib2.Http()))
        logging.debug('Authentication to Google is done')


logging.info('Gathering and aggregating data')
databasefile = os.path.expanduser(cmdline.database)

# Get the temperature for the last 24h
sensorsidx = dict()
i = 1
for sensor in cmdline.sensors:
    sensorsidx[sensor] = i
    i += 1
temperatures = list()
oldmeasurement = [None] * (len(cmdline.sensors) + 1)
with sqlite3.connect(databasefile) as db:
    sql = db.cursor()
    sql.execute("SELECT sensor.sensorid,temperature.temperature,temperature.stamp FROM temperature, sensor WHERE sensor.oid = temperature.sensor AND temperature.stamp >= datetime('now', '-1 day') AND temperature.temperature < 50000 ORDER BY temperature.stamp DESC")
    data = sql.fetchone()
    while data is not None:
        (sensorid, temperature, stamp) = data
        #stamp = stamp.split()[1]
        if oldmeasurement[0] == stamp:
            measurement = oldmeasurement
            temperatures.pop()
        else:
            measurement = [None] * (len(cmdline.sensors) + 1)
            measurement[0] = stamp
        try:
            temperature = str(temperature / 1000)
            measurement[sensorsidx[str(sensorid)]] = temperature
            temperatures.append(measurement)
        except:
            raise
        # Move on
        data = sql.fetchone()
        oldmeasurement = measurement

oauth2json = os.path.expanduser(cmdline.credentials)
oauth2storage = os.path.expanduser(cmdline.store)
logging.info('Authenticating to Google')
gauth = GAuth(oauth2json = oauth2json, oauth2storage = oauth2storage)
gauth.auth()

logging.info('Getting current data from spreadsheet')
result = gauth.service.spreadsheets().values().get(spreadsheetId = cmdline.docid, range = 'DAILY!D2').execute().get('values', [])

rows = int(result[0][0])
logging.debug("There are %s rows in the spreadsheet" % rows)
logging.debug("There are %s rows in the database" % len(temperatures))
measurement = [""] * (len(cmdline.sensors) + 1)
while rows > len(temperatures):
    temperatures.append(measurement)
    rows -= 1
temperatures.append(measurement)
logging.debug("Inserting %s rows into the spreadsheet" % len(temperatures))

logging.info('Saving aggregated data to spreadsheet')
gauth.service.spreadsheets().values().update(spreadsheetId = cmdline.docid, range = 'DAILY!A2',
    #insertDataOption='INSERT_ROWS',
    #insertDataOption='OVERWRITE',
    #valueInputOption='RAW',
    valueInputOption='USER_ENTERED',
    body = {'values': temperatures}).execute()
