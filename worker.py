import os, sys, inspect
import importlib

class Worker:
		def __init__(self, name, config, hubs):
				self.name = name
				self.config = config
				self.hubs = hubs
				self.process = None
				# Make sure the directory of workers is in our modules' path
				cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"workers")))
				if cmd_subfolder not in sys.path:
						sys.path.insert(0, cmd_subfolder)
				# Import the module
				self.m = importlib.import_module(name)

		def start(self):
				self.m.main(self.config, self.hubs)
