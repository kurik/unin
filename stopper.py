#!/usr/bin/env python

try:
    import ConfigParser as configparser # Python 2.x
except ImportError:
    import configparser # Python 3.x
import sqlite3
import optparse
import datetime
import os
from bottle import Bottle, run, request, response, get, abort, static_file, route


CONFIG_FILE = "~/etc/unin_temperature.conf"

# Parse command line
parser = optparse.OptionParser()
parser.add_option("-c", "--cfgfile", dest="cfgfile", help="Config file [%s]" % CONFIG_FILE, metavar="FILE", default=CONFIG_FILE)
parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Be verbose")
(options, args) = parser.parse_args()

# Parse the configuration file
config = configparser.ConfigParser()
config.read(os.path.expanduser(options.cfgfile))

# Open the SQL database
db_name = os.path.expanduser(config.get('DEFAULT','sqlitedb'))
db_name += '.' + datetime.date.today().strftime("%Y-%m")
db = sqlite3.connect(db_name)
sql = db.cursor()

# Handle the REST API

# Global REST API settings
## Allow usage of the REST API from anywhere
response.set_header('Access-Control-Allow-Origin', '*')

@route('/static/<filename:path>')
def send_static(filename):
    # return static_file(filename, root='/home/jkurik/src/unin')
    return static_file(filename, root='.')

@get('/sensors')
def api_sensors():
    # Return the list of sensors
    sensors = ""
    for sensor in sql.execute("SELECT sensorid,note FROM sensor"):
        if sensors != "":
            sensors += ','
        sensors += '{"id": "%s", "description":"%s"}' % sensor
    return '{"sensors": [' + sensors + ']}'

@get('/sensors/<id>')
def api_sensors_details(id):
    # Return details for requested sensor id
    sql.execute("SELECT sensorid,note FROM sensor WHERE sensor.sensorid = ?", (id,))
    sensor = sql.fetchone()
    if sensor is None:
        abort(404, "Sorry, no sensor %s has been found." % (id,))
        return
    return '{"id":"%s", "description":"%s"}' % (sensor[0], sensor[1])

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

    sql.execute("SELECT sensor.sensorid,stamp,temperature FROM temperature,sensor WHERE sensor.oid = temperature.sensor AND sensor.sensorid = ? ORDER BY stamp DESC LIMIT 1", (id,))
    temperature = sql.fetchone()
    if temperature is None:
        abort(404, "Sorry, no temperature has been measured for sensor %s." % (id,))
        return
    return '{"id":"%s", "timestamp":"%s", "temperature":%s}' % temperature

@get('/sensors/<id>/average')
def api_sensors_average(id):
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

    sql.execute("SELECT AVG(temperature) FROM temperature,sensor WHERE sensor.oid = temperature.sensor AND sensor.sensorid = ?", (id,))
    temperature = sql.fetchone()
    if temperature is None:
        abort(404, "Sorry, no temperature has been measured for sensor %s." % (id,))
        return
    return '{"id":"%s", "timestamp":"%s", "temperature":%s}' % (id, "forever", temperature[0])



# Run the server
run(host='localhost', port=8080, debug=True)

