import redis
#from redis._compat import nativestr
import pickle

class RedisSubQ:
		def __init__(self, queue_name, **kwargs):
				self.r = redis.Redis(**kwargs)
				self.q = self.r.pubsub()
				queue_name = [queue_name]
				self.q.execute_command('SUBSCRIBE', *queue_name, **kwargs)
				self.qn = queue_name

		def get(self, block = True):
				self.res = []
				while True:
					m = ''
					while m != b'message':
						self.res = self.q.parse_response()
						m = self.res[0]
					yield pickle.loads(self.res[2])

if __name__ == "__main__":
		rpq = RedisSubQ("TERMO")
		for m in rpq.get():
			print('Response:')
			print('sensor_id:', m['sensor_id'])
			print('temperature:', m['temperature'])
			print('time_stamp:', m['time_stamp'])

