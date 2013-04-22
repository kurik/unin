#!/usr/bin/env python3

import redis_subq
import sqlite3
import time

r = redis_subq.RedisSubQ("TERMO")
try:
	db = sqlite3.connect('termo.db')
	c = db.cursor()
except:
	print('Can not opern SQLite DB')
	exit(0)


for m in r.get():
		print('sensor_id:', m['sensor_id'])
		print('temperature:', m['temperature'])



		f.write(m['sensor_id'] + ',' + time.strftime(
				'%Y-%m-%d %H:%M:%S',
				m['time_stamp']) + ',' + m['temperature'] + '\n')
		f.close()
