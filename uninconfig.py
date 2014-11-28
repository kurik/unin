#!/usr/bin/env python

import datetime
import sys
import os
import glob

CONFIG_FILE = "~/etc/unin_temperature.conf"
DEFAULT_DBNAME = "~/var/unin_temperature.db"
DEFAULT_DBTMP = "/tmp/unin.db"
DEFAULT_GSHEET = "Unin Temperature"
DEFAULT_OUT = "28-000001b4337c"
DEFAULT_IN = "28-000001b4754f"
DEFAULT_CLIENT_SECRET = "unin_temperature.json"
DEFAULT_CLIENT_STORAGE = "unin_temperature.storage"

# Cover the diff in Python v3 x v2 in parsing configs
if sys.version_info[0] == 3:
    # Python 3.x
    import configparser
    class UninConfig_t(configparser.ConfigParser):
        pass
elif sys.version_info[0] == 2:
    # Python 2.x
    import ConfigParser
    class section(object):
        def __init__(self, cfg, sect):
            self.cfg = cfg
            self.sect = sect
        def __getitem__(self, item):
            return self.cfg.get(self.sect, item)
    class UninConfig_t(ConfigParser.ConfigParser):
        def __getitem__(self, sect):
            return section(self, sect)

class UninConfig(UninConfig_t):
    def read(self, filename = CONFIG_FILE):
        if filename is None:
            filename = os.path.expanduser(CONFIG_FILE)
        else:
            filename = os.path.expanduser(filename)
        return UninConfig_t.read(self, filename)

    def get_dbname(self):
        try:
            dbname = self['DEFAULT']['sqlitedb']
        except:
            dbname = DEFAULT_DBNAME
        return os.path.expanduser(dbname + '.' + datetime.date.today().strftime("%Y-%m"))

    def get_dbtmp(self):
        try:
            dbname = self['DEFAULT']['sqlitetmp']
        except:
            dbname = DEFAULT_DBTMP
        return os.path.expanduser(dbname)

    def get_dbs(self):
        try:
            dbname = self['DEFAULT']['sqlitedb']
        except:
            dbname = DEFAULT_DBNAME
        return glob.glob(os.path.expanduser(dbname) + '.20[0-9][0-9]-[0-9][0-9]')

    def get_client_secret(self):
        try:
            f = self['GSHEET']['client_secret']
        except:
            f = DEFAULT_CLIENT_SECRET
        return os.path.expanduser(f)

    def get_client_storage(self):
        try:
            f = self['GSHEET']['client_storage']
        except:
            f = DEFAULT_CLIENT_STORAGE
        return os.path.expanduser(f)
        
    def get_out_sensor(self):
        try:
            return self['GSHEET']['out_sensor']
        except:
            return DEFAULT_OUT
        
    def get_in_sensor(self):
        try:
            return self['GSHEET']['in_sensor']
        except:
            return DEFAULT_IN
        
    def get_gsheet(self):
        try:
            return self['GSHEET']['sheet_name']
        except:
            return DEFAULT_GSHEET
        

if __name__ == '__main__':
    import os
    uc = UninConfig()
    uc.read(CONFIG_FILE)
    print('Database:', uc['DEFAULT']['sqlitedb'])
    print('Database filename:', uc.get_dbname())
    print('Databases:', uc.get_dbs())
