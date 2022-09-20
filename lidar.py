import pycurl
try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
import urllib.request
import json
import time
from socket import *

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

import atexit

Base_URL = 'http://196.254.40.70/cgi/'

def sensor_do(s, url, pf, buf):
    s.setopt(s.URL, url)
    s.setopt(s.POSTFIELDS, pf)
    s.setopt(s.WRITEDATA, buf)
    s.perform()
    rcode = s.getinfo(s.RESPONSE_CODE)
    success = rcode in range(200, 207)
    # print('%s %s: %d (%s)' % (url, pf, rcode, 'OK' if success else 'ERROR'))
    return success

def exit_handler():
    sensor = pycurl.Curl()
    buffer = BytesIO()
    rc = sensor_do(sensor, Base_URL+'reset', urlencode({'data':'reset_system'}), buffer)
    sensor.close()
    port.stopListening()

atexit.register(exit_handler)
    
sensor = pycurl.Curl()
buffer = BytesIO()
rc = sensor_do(sensor, Base_URL+'reset', urlencode({'data':'reset_system'}), buffer)
if rc:
    rc = sensor_do(sensor, Base_URL+'setting', urlencode({'rpm':'600'}), buffer)
if rc:
    rc = sensor_do(sensor, Base_URL+'setting', urlencode({'laser':'on'}), buffer)
sensor.close()

class Echo(DatagramProtocol):
    def datagramReceived(self, data, addr):
        angle = ((data[0x91 - 42] << 8) | data[0x90  - 42])
        time = ((data[0x04DD - 42] << 24) | (data[0x04DC - 42] << 16) | (data[0x04DB - 42] << 8) | data[0x04DA - 42])
        try:
            if self.old_angle > angle:
                log = open("lidar.log", "a")
                if 36000 - self.old_angle < angle:
                    #this is the time in microseconds
                    print(f"{self.old_time}")
                    log.write(str(time) + '\n')
                else:
                    print(f"{time}")
                    log.write(str(time) + '\n') 
                log.close()
        except AttributeError:
            pass

        self.old_angle = angle
        self.old_time = time

port = reactor.listenUDP(2368, Echo())
reactor.run()