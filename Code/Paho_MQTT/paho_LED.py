import os
import shutil
import datetime
import time
import paho.mqtt.client as mqtt

MQTT_SERVER = "192.168.1.112"
MQTT_STATE_PATH = "home/LED_Wall/set"
MQTT_COMMAND_PATH = "home/LED_Wall/status"
STATE_PATH = r"/home/pi/LED_Wall/test_01/state"

MQTT_AUTH_USER = "INSERT_USERNAME"
MQTT_AUTH_PASS = "INSERT_PASSWORD"

rc = 1  # Assume the MQTT has failed


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    #print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.

    client.subscribe(MQTT_STATE_PATH)

    return rc


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):

    payload = msg.payload.decode('utf-8')
    splits = payload.split('"')
    state = splits[3]
    if not state == 'off':
        effect = splits[-2]
        if not effect:
            effect = 'Rain'
        payload = f'{{"state": "{state}", "effect": "{effect}"}}'
    else:
        effect = 'off'
        payload = f'{{"state": "{state}"}}'

    client.publish(MQTT_COMMAND_PATH, payload=str.encode(payload), qos=0, retain=False, properties=None)

    if os.path.isdir(STATE_PATH):
        shutil.rmtree(STATE_PATH)
    os.mkdir(STATE_PATH)
    open(os.path.join(STATE_PATH, effect.replace(" ", "_")), 'a').close()

    if state == 'off':
        from subprocess import call
        call("sudo shutdown -h now", shell=True)


client = mqtt.Client(f"{datetime.datetime.now()}")
client.username_pw_set(username=MQTT_AUTH_USER, password=MQTT_AUTH_PASS)
client.on_connect = on_connect
client.on_message = on_message

while True:
    try:
        rc = client.connect(MQTT_SERVER, 1883, 60)
    except OSError:
        pass

    if not rc:
        break
    time.sleep(1)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
