#!/usr/bin/env python

import uninconfig
import datetime
import sqlite3

uc = uninconfig.UninConfig()
uc.read()

def get_current():
    with sqlite3.connect(uc.get_dbname()) as db:
        sql = db.cursor()
        sql.execute("SELECT MAX(temperature.stamp), sensor.sensorid, temperature.temperature FROM temperature, sensor WHERE sensor.oid = temperature.sensor GROUP BY sensor.sensorid")
        result = dict()
        data = sql.fetchone()
        while data is not None:
            (stamp, sensorid, temperature) = data
            data = sql.fetchone()
            d = {
                "stamp": stamp,
                "sensorid": sensorid,
                "temperature": temperature,
            }
            result["%s.%s" % (str(stamp), str(sensorid))] = d
        return result

def get_daily():
    result = dict()
    for db_name in [uc.get_dbname(), uc.get_dbnameold()]:
        with sqlite3.connect(db_name) as db:
            sql = db.cursor()
            sql.execute("SELECT sensor.sensorid,temperature.temperature,temperature.stamp FROM temperature, sensor WHERE sensor.oid = temperature.sensor AND temperature.stamp >= datetime('now', '-1 day') AND temperature.temperature < 50000")
            data = sql.fetchone()
            while data is not None:
                (sensorid, temperature, stamp) = data
                data = sql.fetchone()
                d = {
                    "sensorid": sensorid,
                    "temperature": temperature,
                    "stamp": stamp,
                }
                result["%s.%s" % (str(stamp), str(sensorid))] = d
    return result

if __name__ == '__main__':
    print('Current:', get_current())
    print('Daily:', get_daily())
