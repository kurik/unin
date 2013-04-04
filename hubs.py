import hub
from multiprocessing import Process

class Hubs:
	def __init__(self, config):
		self.hubs = []
		self.index = 0
		for m in config:
				mobj = hub.Hub(m['name'], m['config'])
				queues = None # TODO
				mobj.process = Process(target = mobj.start)
				self.hubs.append(mobj)

	def __iter__(self):
		return self

	def __next__(self):
		if len(self.hubs) <= self.index:
			raise StopIteration
		else:
			result = self.hubs[self.index]
			self.index += 1
		return result


