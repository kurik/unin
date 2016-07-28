#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import w1_term
import retry
import sqlite3
import logging
import argparse

# A helper formater for argpartse
class SmartFormatter(argparse.HelpFormatter):
    def _split_lines(self, text, width):
        if text.startswith('R|'):
            return text[2:].splitlines()
        # this is the RawTextHelpFormatter._split_lines
        return argparse.HelpFormatter._split_lines(self, text, width)

# Parse command line
parser = argparse.ArgumentParser(add_help = True, formatter_class = SmartFormatter)
group = parser.add_mutually_exclusive_group()
group.add_argument("-v", "--verbose", dest = "verbose", action = 'count', default = 0,
    help = "Be verbose. More -v parameters ensures more verbosity.")
group.add_argument("-q", "--quiet", dest = "verbose", action = 'store_const', const = -1, help = "Be quiet. Print only Errors.")
parser.add_argument("-l", "--log", "--logfile", dest = "logfile", metavar = "FILE", default = "-",
    help = "R|File to log to instead of logging into the stdout.\nTwo characters have a special meaning:\n"
            "':' - log to syslog\n"
            "'-' - log to stdout")
parser.add_argument("-b", "--database", dest = "database", metavar = "FILE", default = '~/var/unin_temperature.db',
    help = "Database file containing the measured values.")
parser.add_argument('-S', "--no-sensor", dest='nosensor', action='store_true', default=False,
    help="Emulate sensors (used for debuging)")
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

# Initialise emulation of sensors if needed
if cmdline.nosensor:
    logging.info("Emulation of sensors has started (no real sensor is used)")
    w1_term.emulation = True

# Read temperature given number of times if needed, to minimise errors on sesors
@retry.retry(3)
def read_temperature(sensors, sensor):
    try:
        return sensors[sensor]
    except Exception as e:
        logging.warning("Measurement on sensor %s has failed: %s" % (sensor, str(e)))
        raise

# Read temperature from all sensors
def read_temperatures():
    logging.debug("Getting a list of available sensors")
    sensors = w1_term.Therms()
    temperatures = {}
    for sensor in sensors:
        try:
            logging.info('Sensor %s starts measuring' % sensor)
            temperatures[sensor] = read_temperature(sensors, sensor)
            logging.info('Sensor %s measured: %s' % (sensor, temperatures[sensor]))
        except Exception as e:
            logging.error('Reading of temperature on sensor %s has failed: %s' % (sensor, str(e)))
    return temperatures

# Save temperature to SQLite
def save_to_db(temperatures):
    try:
        logging.debug("Opening database %s" % cmdline.database)
        with sqlite3.connect(cmdline.database) as db:
            sql = db.cursor()
            # Make sure we have all tables defined
            sql.execute("CREATE TABLE IF NOT EXISTS sensor(sensorid TEXT UNIQUE, note TEXT)")
            sql.execute("CREATE TABLE IF NOT EXISTS temperature(stamp TEXT DEFAULT (datetime('now','localtime')), temperature REAL, sensor INTEGER)")

            # Go throught all we have from sensors
            for sensor in temperatures:
                # Do we have the sensor in DB ?
                logging.debug("Checking whether sensor %s in already the dabatase" % sensor)
                sql.execute("SELECT oid FROM sensor WHERE sensorid = ?", (sensor,))
                oid = sql.fetchone()
                if oid is None:
                    # We need to insert the sensor into DB
                    logging.info("Inserting nonexisting sensor %s into the dabatase" % sensor)
                    sql.execute("INSERT INTO sensor(sensorid) VALUES(?)", (sensor,))
                    # Get the OID
                    oid = sql.lastrowid
                    logging.debug("Sensor %s registered in database as OID=%s" % (sensor, oid))
                else:
                    oid = oid[0]
                # Save the temperature
                logging.debug("Saving measured value (%s) for sensor %s into database" % (temperatures[sensor], sensor))
                sql.execute("INSERT INTO temperature(sensor, temperature) VALUES(?,?)", (oid, temperatures[sensor]))
            logging.info('Measured values from %s sensors were saved in database' % len(temperatures))
    except Exception as e:
        logging.error('Database error: %s' % str(e))

# Read temperatures
temperatures = read_temperatures()
# Save to DB
save_to_db(temperatures)

