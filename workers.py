import worker
from multiprocessing import Process

class Workers:
	def __init__(self, config):
		self.workers = []
		self.index = 0
		for m in config:
				mobj = worker.Worker(m['name'], m['config'])
				queues = None # TODO
				mobj.process = Process(target = mobj.start, args = (queues,))
				self.workers.append(mobj)

	def __iter__(self):
		return self

	def __next__(self):
		if len(self.workers) <= self.index:
			raise StopIteration
		else:
			result = self.workers[self.index]
			self.index += 1
		return result


