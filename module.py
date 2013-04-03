import importlib

class Module:
		def __init__(self, name, config):
				self.name = name
				self.config = config
				self.process = None
				self.m = importlib.import_module(name)
				print('Module name:', name, 'created')

		def start(self, queues):
				self.queues = queues
				self.m.main(queues)
