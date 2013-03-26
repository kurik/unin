# w1_therm python module

# The place, used by w1_therm module for communication with user space
w1_sys_bus = '/sys/bus/w1/devices'

import os

# A class reading the temperature from w1_therm module for a given sensor
# It is returned from Therms when iterrating through list of available sensors, or created
# from ID of the sensor
class Therm:
	def __init__(self, therm_id): # The therm_id is a sensor ID (check /sys/bus/w1/devices/ )
		self.therm_id = therm_id

	def getId(self):
		return self.therm_id

	def getDegrees(self):
		th_file = w1_sys_bus + '/' + self.therm_id + '/w1_slave'
		degrees = open(th_file, 'r').read().split()[-1]
		if degrees[:2] == 't=':
			return degrees[2:]
		else:
			return '?'



# An iterator class to walk through therm sensors
class Therms:
	def __init__(self):
		self.therm_list = []
		self.index = 0

	def __iter__(self):
		return self

	def __next__(self):
		if self.therm_list == []:
			self.list()
		if len(self.therm_list) <= self.index:
			raise StopIteration
		else:
			result = self.therm_list[self.index]
			self.index += 1
			return Therm(result)

	def list(self):
		self.therm_list = []
		for d in os.listdir(w1_sys_bus):
			if d[:3] != 'w1_':
				self.therm_list.append(d)
		return self.therm_list


if __name__ == "__main__":
	for t in Therms():
		print(t.getDegrees())
