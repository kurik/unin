#!/usr/bin/env python

import w1_term
import retry
import sqlite3
import configparser
import os
import optparse

CONFIG_FILE="~/etc/unin_temperature.conf"

parser = optparse.OptionParser()
parser.add_option("-c", "--cfgfile", dest="cfgfile", help="Config file [%s]" % CONFIG_FILE, metavar="FILE", default=CONFIG_FILE)
parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Be verbose")
(options, args) = parser.parse_args()

# Read temperature given number of times, if needed, to minimise errors on sesors
@retry.retry(3)
def read_temperature(sensors, sensor):
    return sensors[sensor]

# Parse the configuration file
config = configparser.ConfigParser()
config.read(os.path.expanduser(options.cfgfile))

# Make ready for read of temperature
sensors = w1_term.Therms()

# Open SQLite database
with sqlite3.connect(os.path.expanduser(config['DEFAULT']['sqlitedb'])) as db:
    sql = db.cursor()
    # Make sure we have all tables defined
    sql.execute("CREATE TABLE IF NOT EXISTS sensor(sensorid TEXT UNIQUE)")
    sql.execute("CREATE TABLE IF NOT EXISTS temperature(stamp TEXT DEFAULT (datetime('now')), temperature REAL, sensor INTEGER)")

    # Go throught all we have from sensors
    for sensor in sensors:
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
        if options.verbose:
            print('Saving temperature of sensor %s' % sensor)
        sql.execute("INSERT INTO temperature(sensor, temperature) VALUES(?,?)", (oid, read_temperature(sensors, sensor)))
