# ci-msg-parser

Python library for parsing NSRTW_mk4 MQTT protocol messages.

### Quick-Start

Note these instructions are for testing/demo purposes only.

To start, you will need an MQTT server:

```
$ cat <<EOF > mosquitto.conf
listener 1883 0.0.0.0
allow_anonymous true
EOF

$ docker run --rm -it -p 1883:1883 -v "./mosquitto.conf:/mosquitto/config/mosquitto.conf" eclipse-mosquitto
```

Make sure your NSRTW_mk4 is configured to connect to your MQTT server.

Next, use a python script to receive and process messages the instrument:

```
#!/usr/bin/env python

import paho.mqtt.client as mqtt
from ci_msg_parser import *

def on_connect(client, userdata, flags, reason_code, properties):
    client.subscribe("#")

def on_message(client, userdata, msg):
    parsed = MessageParser.parse(msg.payload)
    if isinstance(parsed, VitalSignsMessage):
        print(f"rssi: {parsed.rssi} batt: {parsed.battery_voltage} temp: {parsed.temperature}")
	if isinstance(parsed, RecordedDataMessage):
	    print(f"values: {parsed.values}")

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect("localhost", 1883, 60)
mqttc.loop_forever()
```

```
$ pip install paho-mqtt ci-msg-parser
$ python script.py
```
