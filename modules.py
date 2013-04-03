import module

class Modules:
	def __init__(self, config):
		self.modules = []
		self.index = 0
		for m in config:
				self.modules.append(module.Module(m['name'], m['config']))

	def __iter__(self):
		return self

	def __next__(self):
		if len(self.modules) <= self.index:
			raise StopIteration
		else:
			result = self.modules[self.index]
			self.index += 1
		return Module(result)


