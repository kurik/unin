import redis
from redis._compat import nativestr

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
					m_t = ''
					while m_t != 'message':
						self.res = self.q.parse_response()
						m_t = nativestr(self.res[0])
					yield nativestr(self.res[2])

rpq = RedisSubQ("Test")
for m in rpq.get():
	print('Response:', m)

