import redis

class RedisPubQ:
		def __init__(self, queue_name, **kwargs):
				self.r = redis.Redis(**kwargs)
				self.qn = queue_name

		def publish(self, message):
			self.r.execute_command('PUBLISH', self.qn, message)

rpq = RedisPubQ("Test")
rpq.publish("Uaaaaaaa")

