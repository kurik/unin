#!/usr/bin/env python

try:
    import ConfigParser as configparser # Python 2.x
except ImportError:
    import configparser # Python 3.x
import sqlite3
import optparse
import datetime
import os
from bottle import Bottle, run, request, response, get


CONFIG_FILE="~/etc/unin_temperature.conf"

# Parse command line
parser = optparse.OptionParser()
parser.add_option("-c", "--cfgfile", dest="cfgfile", help="Config file [%s]" % CONFIG_FILE, metavar="FILE", default=CONFIG_FILE)
parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Be verbose")
(options, args) = parser.parse_args()

# Parse the configuration file
config = configparser.ConfigParser()
config.read(os.path.expanduser(options.cfgfile))

# Open the SQL database


# Handle the REST API

@get('/')
def api_root():
    # Return redirection to the API
    return "Hello World!"

@get('/sensors')
def api_sensors():
    # Return the list of sensors
    return 'List of sensors:'

@get('/sensors/<id>')
def api_sensors_details(id):
    # Return details for requested sensor id
    return 'Sensor id:', id

@get('/sensors/<id>/temperature')
def api_sensors_temperature(id):
    # Return details for requested sensor id
    try:
        since = request.query.since
    except:
        since = None
    try:
        to = request.query.to
    except:
        to = None
    return 'Sensor id:', id, '\n<br>since:', since, '\n<br>to:', to

@get('/sensors/<id>/average')
def api_sensors_temperature(id):
    # Return details for requested sensor id
    try:
        since = request.query.since
    except:
        since = None
    try:
        to = request.query.to
    except:
        to = None
    try:
        granularity = request.query.granularity
    except:
        granularity = None
    return 'Sensor id:', id, '\n<br>since:', since, '\n<br>to:', to, '\n<br>granularity:', granularity

# Run the server
run(host='localhost', port=8080, debug=True)

