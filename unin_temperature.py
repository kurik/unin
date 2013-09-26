#!/usr/bin/env python

import w1_term
import retry
import sqlite3
import configparser
import os
import optparse
import gspread
import datetime
from multiprocessing import Pool


CONFIG_FILE="~/etc/unin_temperature.conf"

# Parse command line
parser = optparse.OptionParser()
parser.add_option("-c", "--cfgfile", dest="cfgfile", help="Config file [%s]" % CONFIG_FILE, metavar="FILE", default=CONFIG_FILE)
parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Be verbose")
(options, args) = parser.parse_args()

# Parse the configuration file
config = configparser.ConfigParser()
config.read(os.path.expanduser(options.cfgfile))

# Read temperature given number of times if needed, to minimise errors on sesors
@retry.retry(3)
def read_temperature(sensors, sensor):
    return sensors[sensor]

# Read temperature from all sensors
def read_temperatures():
    sensors = w1_term.Therms()
    temperatures = {}
    for sensor in sensors:
        temperatures[sensor] = read_temperature(sensors, sensor)
        if options.verbose:
            print('Reading temperature of sensor %s' % sensor)
    return temperatures

# Save temperature to SQLite
def save_to_db(config, temperatures):
    if options.verbose:
        print('Going to save temperature into DB ... ',)
    with sqlite3.connect(os.path.expanduser(config['DEFAULT']['sqlitedb'])) as db:
        sql = db.cursor()
        # Make sure we have all tables defined
        sql.execute("CREATE TABLE IF NOT EXISTS sensor(sensorid TEXT UNIQUE, note TEXT)")
        sql.execute("CREATE TABLE IF NOT EXISTS temperature(stamp TEXT DEFAULT (datetime('now')), temperature REAL, sensor INTEGER)")

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

    if options.verbose:
        print('DONE')

# Save the temperature to Google spreadsheet
def save_to_gsheet(config, temperatures):
    if options.verbose:
        print('Saving temperature to Google spreadsheet ... ',)
    gc = gspread.login(config['GSHEET']['user'], config['GSHEET']['password'])
    spreadsheet = gc.open(config['GSHEET']['sheet_name'])
    w_summary = spreadsheet.worksheet('SUMMARY')
    now = datetime.datetime.now()
    w_summary.update_acell('B2', float(temperatures[config['GSHEET']['out_sensor']]) / 1000)
    w_summary.update_acell('C2', float(temperatures[config['GSHEET']['in_sensor']]) / 1000)
    w_summary.update_acell('A1', now.strftime("%Y-%m-%d\n%H:%M"))
    if options.verbose:
        print('DONE')

# Read temperatures
temperatures = read_temperatures()
# Prepare processes for saving data in paralel
pool = Pool(processes=2)
# Save to DB
db_result = pool.apply_async(save_to_db, (config, temperatures))
# Save to GSheet
gs_result = pool.apply_async(save_to_gsheet, (config, temperatures))
# Wait till the saving process are completed
db_result.get(timeout=30)
gs_result.get(timeout=60)

