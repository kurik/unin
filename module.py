import os, sys, inspect
import importlib

class Module:
		def __init__(self, name, config):
				self.name = name
				self.config = config
				self.process = None
				# Make sure the directory of modules is in our modules' path
				cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"modules")))
				if cmd_subfolder not in sys.path:
						sys.path.insert(0, cmd_subfolder)
				# Import the module
				self.m = importlib.import_module(name)

		def start(self, queues):
				self.queues = queues
				self.m.main(queues)
