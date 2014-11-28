#!/usr/bin/env python

import w1_term
import retry
import sqlite3
import os
import optparse
import datetime
import sys
import uninconfig
import uninlog
from uninlog import log_info, log_err

# Parse command line
parser = optparse.OptionParser()
parser.add_option("-c", "--cfgfile", dest="cfgfile", help="Config file [%s]" % uninconfig.CONFIG_FILE, metavar = "FILE", default = None)
parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Be verbose on console and do not use syslog.")
parser.add_option("-S", "--no-sensor", action="store_true", dest="nosensor", default=False,
    help="No sensors available (used for debugigng)")
(options, args) = parser.parse_args()

# Initialise emulation of sensors if needed
if options.nosensor:
    w1_term.emulation = True

# Initialize logging
uninlog.console = options.verbose

# Parse the config file
config = uninconfig.UninConfig()
config.read(options.cfgfile)

# Read temperature given number of times if needed, to minimise errors on sesors
@retry.retry(3)
def read_temperature(sensors, sensor):
    return sensors[sensor]

# Read temperature from all sensors
def read_temperatures():
    sensors = w1_term.Therms()
    temperatures = {}
    for sensor in sensors:
        try:
            temperatures[sensor] = read_temperature(sensors, sensor)
            log_info('Sensor %s measured: %s' % (sensor, temperatures[sensor]))
        except Exception as e:
            log_err('Reading of temperature %s failed: %s' % (sensor, str(e)))
    return temperatures

# Save temperature to SQLite
def save_to_db(config, temperatures):
    try:
        db_name = config.get_dbname()
        with sqlite3.connect(db_name) as db:
            sql = db.cursor()
            # Make sure we have all tables defined
            sql.execute("CREATE TABLE IF NOT EXISTS sensor(sensorid TEXT UNIQUE, note TEXT)")
            sql.execute("CREATE TABLE IF NOT EXISTS temperature(stamp TEXT DEFAULT (datetime('now','localtime')), temperature REAL, sensor INTEGER)")

            # Go throught all we have from sensors
            for sensor in temperatures:
                # Do we have the sensor in DB ?
                sql.execute("SELECT oid FROM sensor WHERE sensorid = ?", (sensor,))
                oid = sql.fetchone()
                if oid is None:
                    # We need to insert the sensor into DB
                    sql.execute("INSERT INTO sensor(sensorid) VALUES(?)", (sensor,))
                    # Get the OID
                    oid = sql.lastrowid
                else:
                    oid = oid[0]
                # Save the temperature
                sql.execute("INSERT INTO temperature(sensor, temperature) VALUES(?,?)", (oid, temperatures[sensor]))
            log_info('Values succesfully saved to DB: %s' % (db_name))
    except Exception as e:
        log_err('Database error: %s' % (str(e)))

# Read temperatures
temperatures = read_temperatures()
# Save to DB
save_to_db(config, temperatures)

