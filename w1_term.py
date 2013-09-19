#!/usr/bin/env python
# w1_therm python module

import os

# The place, used by w1_therm module for communication with user space
w1_sys_bus = '/sys/bus/w1/devices'

# If set to True, returns emulated values instead of real data from sensors
# Use for testing on non-RaspberryPi
emulation = False

emulatedData = {
    '28-000001b4337c':'2a 01 4b 46 7f ff 06 10 16 : crc=16 YES\n2a 01 4b 46 7f ff 06 10 16 t=18625',
    '28-000001b43eb4':'ff ff ff ff ff ff ff ff ff : crc=c9 NO\n0a 01 4b 46 7f ff 06 10 be t=-62',
    '28-000001b43eba':'0b 01 4b 46 7f ff 05 10 a8 : crc=a8 YES\n0b 01 4b 46 7f ff 05 10 a8 t=16687',
    '28-000001b4754f':'45 01 4b 46 7f ff 0b 10 84 : crc=84 YES\n45 01 4b 46 7f ff 0b 10 84 t=20312',
}

# Handling exceptions from termal sensors
class ThermException(IOError):
    pass

# An iterator class to walk through therm sensors
#class _Therms_Iterator(object):
class _Therms_Iterator():
    def __init__(self):
        self.index = -1
        if emulation:
            self.keys = [x for x in emulatedData]
        else:
            for (dirpath, dirnames, filenames) in os.walk(w1_sys_bus):
                self.keys = [x for x in dirnames if 'w1_bus' not in x]

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        if len(self.keys) > (self.index + 1):
            self.index += 1
        else:
            raise StopIteration()

        return self.keys[self.index]

# Container 
class Therms():
    def __getitem__(self, key):
        sensor_path = w1_sys_bus + '/' + str(key) + '/w1_slave'
        sensor_data = ""
        if emulation:
            sensor_data = emulatedData[key]
        elif os.path.exists(sensor_path):
            try:
                with open(sensor_path, 'r') as sensor:
                    sensor_data = sensor.read()
            except IOError as e:
                raise ThermException("Error reading from sensor %s: (%s)" % (key, e.strerror))
        else:
            raise KeyError('Sensor %s is not available' % key)

        # Return read temperature or raise an error if a problem occures
        sensor_data = sensor_data.split()
        degrees = sensor_data[-1]
        status = sensor_data[11]
        if (degrees[:2] != 't=') or (status.upper() != 'YES'):
            raise ThermException('Temperature sensor %s reported an error\nDegrees: %s\nStatus: %s' % (key, degrees, status))
        return degrees[2:]

    def __setitem__(self, key, value):
        raise AttributeError("Sensor %s is read-only" % key)

    def __delitem__(self, key):
        raise AttributeError("Can not delete sensor %s" % key)

    def __contains__(self, key):
        return os.path.exists(w1_sys_bus + '/' + str(key) + '/w1_slave')

    def __iter__(self):
        return _Therms_Iterator()

    def __len__(self):
        for (dirpath, dirnames, filenames) in os.walk(w1_sys_bus):
            return len(dirnames) - 1


if __name__ == "__main__":
    import sys
    emulation = True
    sensors = Therms()
    for t in sensors:
        try:
            temp = sensors[t]
            print('Sensor %s: %s' % (t, temp))
            sys.stdout.flush()
        except Exception as e:
            print('Error reading sensor %s (%s)' % (t, e.strerror))
            sys.stdout.flush()
