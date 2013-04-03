import module
from multiprocessing import Process

class Modules:
	def __init__(self, config):
		self.modules = []
		self.index = 0
		for m in config:
				mobj = module.Module(m['name'], m['config'])
				queues = None # TODO
				mobj.process = Process(target = mobj.start, args = (queues,))
				self.modules.append(mobj)

	def __iter__(self):
		return self

	def __next__(self):
		if len(self.modules) <= self.index:
			raise StopIteration
		else:
			result = self.modules[self.index]
			self.index += 1
		return result


