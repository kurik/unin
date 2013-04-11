from hotqueue import HotQueue
import time

queue = HotQueue("temperature", host="localhost", port=6379, db=0)

@queue.worker
def save_csv(dataset):
		print('Time stamp:',
						time.strftime('%Y-%m-%d %H:%M:%S',
								dataset['time_stamp']))
		print('Sensor ID:', dataset['sensor_id'])
		print('Temperature:', dataset['temperature'])
		print()

save_csv()
