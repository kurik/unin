#!/usr/bin/env python

import w1_term
import retry
import sqlite3
import configparser
import os

CONFIG_FILE="~/etc/unin_temperature.conf"

# Read temperature given number of times, if needed, to minimise errors on sesors
@retry.retry(3)
def __read_temperature(sensors, sensor):
    return sensors[sensor]

# Parse the configuration file
config = configparser.ConfigParser()
config.read(os.path.expanduser(CONFIG_FILE))

# Read the temperature
sensors = w1_term.Therms()
temperatures = {}
for sensor in sensors:
    temperatures[sensor] = __read_temperature(sensors, sensor)

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
        sql.execute("INSERT INTO temperature(sensor, temperature) VALUES(?,?)", (oid, temperatures[sensor]))

