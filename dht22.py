#!/usr/bin/python
# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


# Informationen im Rahmen der Projektarbeit
#
# Auf Basis folgender Libraries:
# - Adafruit_Python_DHT von Adafruit (git clone https://github.com/adafruit/Adafruit_Python_DHT.git)
# - iot_sensor.py von influxdata (https://raw.githubusercontent.com/influxdata/influxdb-client-python/master/examples/iot_sensor.py)
#
# Änderungen
# - reactivex entfernt
# - influxxdb api token generiert
# - variablen angepasst
# - logik vereinfacht
# - getestet mit systemd
# - debug auf False gesetzt
#
# Wichtig: 
# Mir ist bewusst, dass der API-Token geheim gehalten werden sollte. 
# Da es sich jedoch um ein Test-System handelt welches nur in meinem
# internen LAN ist, sehe ich kein Problem darin, den API Key zu 
# veröffentlichen.

import Adafruit_DHT
import atexit
import socket
import time
from sys import exit
from datetime import timedelta
from influxdb_client import WriteApi, WriteOptions
from influxdb_client.client.influxdb_client import InfluxDBClient

vGpio = 4
vUri = "http://127.0.0.1:8086"
vOrg = "privat"
# token in git history ist zum testen ;)
vToken = "..."
vBucket = "dht22"
vDebug = False

def on_exit(db_client: InfluxDBClient, write_api: WriteApi):
    write_api.close()
    db_client.close()


_db_client = InfluxDBClient(url=vUri, token=vToken, org=vOrg, debug=vDebug)

humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, vGpio)
if humidity is not None and temperature is not None:
    _write_api = _db_client.write_api(write_options=WriteOptions(batch_size=1))
    data = 'temperature,hostname={},type=float value={}'.format(socket.gethostname(), temperature)
    _write_api.write(bucket=vBucket, record=data)
    data = 'humidity,hostname={},type=float value={}'.format(socket.gethostname(), humidity)
    _write_api.write(bucket=vBucket, record=data)
else:
    print('Failed to get reading. Try again!')
    sys.exit(1)
atexit.register(on_exit, _db_client, _write_api)

time.sleep(1)
