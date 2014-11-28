#!/usr/bin/env python

import datetime
import sys
import os

CONFIG_FILE = "~/etc/unin_temperature.conf"

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
        return os.path.expanduser(self['DEFAULT']['sqlitedb'] + '.' + datetime.date.today().strftime("%Y-%m"))

if __name__ == '__main__':
    import os
    uc = UninConfig()
    uc.read(CONFIG_FILE)
    print('Database:', uc['DEFAULT']['sqlitedb'])
    print('Database filename:', uc.get_dbname())
