#!/usr/bin/env python

import uninconfig
import datetime
import sqlite3
import os

uc = uninconfig.UninConfig()
uc.read()

today = datetime.date.today().strftime("%Y-%m")
dbs = [f for f in uc.get_dbs() if f[-7:] <= today]

def init_db():
    with sqlite3.connect(uc.get_dbtmp()) as db:
        sql = db.cursor()
        sql.execute("ATTACH DATABASE '" + uc.get_dbtmp() + "' AS m")
        sql.execute("CREATE TABLE IF NOT EXISTS m.sensor(sensorid TEXT UNIQUE, note TEXT)")
        sql.execute("CREATE TABLE IF NOT EXISTS m.temperature(stamp TEXT, temperature REAL, sensor INTEGER)")

        for fdb in dbs:
            dbid = 'db' + fdb[-7:-3] + fdb[-2:]
            sql.execute("ATTACH DATABASE '" + fdb + "' AS " + dbid)
            sql.execute("INSERT INTO m.temperature SELECT * FROM " + dbid + ".temperature")
            try:
                sql.execute("INSERT INTO m.sensor SELECT * FROM " + dbid + ".sensor")
            except sqlite3.IntegrityError as e:
                pass
            sql.execute("DETACH DATABASE " + dbid)

def update_db():
    with sqlite3.connect(uc.get_dbtmp()) as db:
        sql = db.cursor()
        sql.execute("ATTACH DATABASE '" + uc.get_dbtmp() + "' AS m")
        sql.execute("ATTACH DATABASE '" + uc.get_dbname() + "' AS c")
        sql.execute("INSERT INTO m.temperature SELECT * FROM c.temperature WHERE (SELECT max(m.temperature.stamp) FROM m.temperature) < c.temperature.stamp")

def get_current():
    with sqlite3.connect(uc.get_dbtmp()) as db:
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
            result[sensorid] = d
        return result

def get_aggr(days):
    with sqlite3.connect(uc.get_dbtmp()) as db:
        sql = db.cursor()
        sql.execute("SELECT sensor.sensorid,MIN(temperature.temperature),AVG(temperature.temperature),MAX(temperature.temperature) FROM temperature, sensor WHERE sensor.oid = temperature.sensor AND stamp >= datetime('now', '-%s day') AND temperature.temperature < 50000 GROUP BY sensor.sensorid" % str(days))
        result = dict()
        data = sql.fetchone()
        while data is not None:
            (sensorid, tmin, tavg, tmax) = data
            data = sql.fetchone()
            d = {
                "sensorid": sensorid,
                "min": tmin,
                "avg": tavg,
                "max": tmax,
            }
            result[sensorid] = d
        return result

# Initialize temp DB if needed
try:
    statinfo = os.stat(uc.get_dbtmp())
    st_size = statinfo.st_size
except:
    st_size = 0
if st_size < 8100:
    try:
        os.unlink(uc.get_dbtmp())
    except:
        pass
    init_db() # Initialize DB
else:
    update_db() # Update DB

