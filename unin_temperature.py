#!/usr/bin/env python

import w1_term
import retry
import sqlite3
import os
import optparse
import datetime
import sys
import syslog
from syslog import LOG_EMERG, LOG_ALERT, LOG_CRIT, LOG_ERR, LOG_WARNING, LOG_NOTICE, LOG_INFO, LOG_DEBUG

CONFIG_FILE="~/etc/unin_temperature.conf"

# Parse command line
parser = optparse.OptionParser()
parser.add_option("-c", "--cfgfile", dest="cfgfile", help="Config file [%s]" % CONFIG_FILE, metavar="FILE", default=CONFIG_FILE)
parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Be verbose on console and do not use syslog.")
parser.add_option("-S", "--no-sensor", action="store_true", dest="nosensor", default=False,
    help="No sensors available (used for debugigng)")
(options, args) = parser.parse_args()

# Initialize syslog
syslog.openlog('temperature', 0, syslog.LOG_USER)

# Initialise emulation of sensors if needed
if options.nosensor:
    w1_term.emulation = True

# Parse the config file
if sys.version_info[0] == 3:
    # Python 3.x
    import configparser
    config = configparser.ConfigParser()
elif sys.version_info[0] == 2:
    # Python 2.x
    import ConfigParser
    class section(object):
        def __init__(self, cfg, section):
            self.cfg = cfg
            self.section = section
        def __getitem__(self, item):
            return self.cfg.get(self.section, item)
    class configparser(ConfigParser.ConfigParser):
        def __getitem__(self, sect):
            return section(self, sect)
    config = configparser()

config.read(os.path.expanduser(options.cfgfile))

# Read temperature given number of times if needed, to minimise errors on sesors
@retry.retry(3)
def read_temperature(sensors, sensor):
    return sensors[sensor]

def log(msg, level = LOG_INFO):
    if options.verbose:
        print(('EMERG', 'ALERT', 'CRIT', 'ERR', 'WARNING', 'NOTICE', 'INFO', 'DEBUG')[level] + ':', msg)
    else:
        syslog.syslog(level, msg)

# Read temperature from all sensors
def read_temperatures():
    sensors = w1_term.Therms()
    temperatures = {}
    for sensor in sensors:
        try:
            temperatures[sensor] = read_temperature(sensors, sensor)
            log('Sensor %s measured: %s' % (sensor, temperatures[sensor]))
        except Exception as e:
            log('Reading of temperature %s failed: %s' % (sensor, str(e)), LOG_ERR)
    return temperatures

# Save temperature to SQLite
def save_to_db(config, temperatures):
    db_name = os.path.expanduser(config['DEFAULT']['sqlitedb'])
    db_name += '.' + datetime.date.today().strftime("%Y-%m")
    try:
        with sqlite3.connect(db_name) as db:
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
            log('Values succesfully saved to DB: %s' % (db_name))
    except Exception as e:
        log('Database error: %s' % (str(e)), LOG_ERR)

# Read temperatures
temperatures = read_temperatures()
# Save to DB
save_to_db(config, temperatures)

