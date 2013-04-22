import redis_pubq
import w1_term
import time

r = redis_pubq.RedisPubQ('TERMO')
ts = w1_term.Therms()

while True:
		for t in ts:
				msg = {'sensor_id': t.getId(),
								'temperature': t.getDegrees(),
								'time_stamp': time.gmtime()}
				r.publish(msg)
		time.sleep(60)
		ts = w1_term.Therms()
