import os

def main(config, hubs):
		print('Inside the worker', __name__, ':: PID = ', os.getpid())
		print('  Hubs:', len(hubs.hubs))
		print('  Config =', config)
