# ci-msg-parser

Python library for parsing NSRTW_mk4 MQTT protocol messages.

### Usage

```
#!/usr/bin/env python

import paho.mqtt.client as mqtt
from ci_msg_parser import *

def on_connect(client, userdata, flags, reason_code, properties):
    client.subscribe("NS/NSRTW_mk4_MQTT/FW17/*")

def on_message(client, userdata, msg):
    parsed = MessageParser.parse(msg.payload)
	

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect("localhost", 1883, 60)
mqttc.loop_forever()
```
