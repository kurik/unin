class Module:
		def __init__(self, name, config):
				self.name = name
				self.config = config
				self.process = None
				print('Module name:', name, 'created')

		def start(self, queues):
				self.queues = queues
				print('Module', self.name, 'running')
