import redis
import pickle
#import time

class RedisPubQ:
		def __init__(self, queue_name, **kwargs):
				self.r = redis.Redis(**kwargs)
				self.qn = queue_name

		def publish(self, message):
			message = pickle.dumps(message)
			#message = map(pickle.dumps, message)
			self.r.execute_command('PUBLISH', self.qn, message)

if __name__ == "__main__":
		import time
		rpq = RedisPubQ("TERMO")
		rpq.publish({'sensor_id': '28-000001b4337c',
				'temperature': 12000,
				'time_stamp': time.gmtime()})

