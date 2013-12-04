#!/usr/bin/env python

import sqlite3
import configparser
import optparse
import datetime
from bottle import Bottle, run


CONFIG_FILE="~/etc/unin_temperature.conf"

# Parse command line
parser = optparse.OptionParser()
parser.add_option("-c", "--cfgfile", dest="cfgfile", help="Config file [%s]" % CONFIG_FILE, metavar="FILE", default=CONFIG_FILE)
parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Be verbose")
(options, args) = parser.parse_args()

# Parse the configuration file
config = configparser.ConfigParser()
config.read(os.path.expanduser(options.cfgfile))

