#!/usr/bin/env python3

import redis_subq
import time

r = redis_subq.RedisSubQ("TERMO")
for m in r.get():
		f = open('termo.csv', 'a')
		print('sensor_id:', m['sensor_id'])
		print('temperature:', m['temperature'])

		f.write(m['sensor_id'] + ',' + time.strftime(
				'%Y-%m-%d %H:%M:%S',
				m['time_stamp']) + ',' + m['temperature'] + '\n')
		f.close()
