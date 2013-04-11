from hotqueue import HotQueue
import time

queue = HotQueue("temperature", host="localhost", port=6379, db=0)

#while True:
queue.put({'sensor_id': '28-000001b4337c',
	'temperature': 12000,
	'time_stamp': time.gmtime()})
queue.put({'sensor_id': '28-000001b4754f',
	'temperature': 5000,
	'time_stamp': time.gmtime()})
queue.put({'sensor_id': '28-000001b43eba',
	'temperature': -1000,
	'time_stamp': time.gmtime()})
#time.sleep(1)
