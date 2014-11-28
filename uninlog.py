#!/usr/bin/env python

import syslog
from syslog import LOG_EMERG, LOG_ALERT, LOG_CRIT, LOG_ERR, LOG_WARNING, LOG_NOTICE, LOG_INFO, LOG_DEBUG

# Initialize syslog
syslog.openlog('temperature', 0, syslog.LOG_USER)

console = False

def log(msg, level = LOG_INFO):
    if console:
        print(('EMERG', 'ALERT', 'CRIT', 'ERR', 'WARNING', 'NOTICE', 'INFO', 'DEBUG')[level] + ':', msg)
    else:
        syslog.syslog(level, msg)

def log_err(msg):
    log(msg, LOG_ERR)
def log_info(msg):
    log(msg, LOG_INFO)
