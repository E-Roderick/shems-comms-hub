"""
File: dummy_client.py
Email: e.roderick@uqconnect.edu.au
Description: A dummy client script to emulate a SHEMS device. Created for demo
    purposes.
"""

from threading import Timer
import os
import time

import paho.mqtt.client as mqtt


MQTT_PORT = 1883
MQTT_TOPIC_NOTIFY = "shem/ntfy/"
MQTT_TOPIC_DEVICE = "shem/dev/"
MQTT_TOPIC_ALARM= "shem/alm/"
DEVICE_ID = "demo_shems_client"

def alarm_cb(client):
    """ Callback to change LEDs and send an alarm to MQTT broker """
    print("Sending alarm")
    # Disable green LED
    os.system("/shems/rpi-utils/led-green-off.sh")
    # Enable red LED
    os.system("/shems/rpi-utils/led-red-on.sh")
    # Send charge alarm
    alarm_data = f'{DEVICE_ID},opChargeStatus,{time.time()},0.25,0.25'
    client.publish(MQTT_TOPIC_ALARM, alarm_data)


def on_connect(client, userdata, flags, rc):
    """ callback for CONNACK response from server """
    print("connected with result", str(rc))
    client.subscribe(MQTT_TOPIC_NOTIFY)


def on_message(client, userdata, msg):
    """ Callback for when PUBLISH message is received from server """
    print(f"Received {msg.payload} from {msg.topic}")

    if msg.topic == MQTT_TOPIC_NOTIFY:
        # Enable green LED
        os.system("/shems/rpi-utils/led-green-on.sh")
        # Schedule alarm
        Timer(5, alarm_cb, args=(client,)).start()


def main():
    """ Simulate a SHEMS client device. Will connect to the MQTT broker and wait
        for a NOTIFY message. On receipt, will turn on a green LED. Five seconds
        after receipt, will swap to a red LED and send an ALARM.
    """
    # Disable all LEDs
    os.system("/shems/rpi-utils/led-off.sh")

    broker_addr = input("Enter broker address: ")

    client = mqtt.Client(DEVICE_ID)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(broker_addr, MQTT_PORT)

    # Notify controller of device existence
    data = f'{DEVICE_ID},192.168.10.10,A demo shems device,{time.time()},0.98'
    client.publish(MQTT_TOPIC_DEVICE, data)

    # Wait for messages
    client.loop_forever()

if __name__ == "__main__":
    main()
