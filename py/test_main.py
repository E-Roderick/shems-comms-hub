"""
File: test_main.py
Email: e.roderick@uqconnect.edu.au
Description: Main file for quick testing and demos.
"""

import paho.mqtt.client as mqtt
from common.env_vars import MQTT_ADDR, MQTT_PORT

def main():
    """ Simulate a SHEMS client device. Will connect to the MQTT broker and wait
        for a NOTIFY message. On receipt, will turn on a green LED. Five seconds
        after receipt, will swap to a red LED and send an ALARM.
    """
    client = mqtt.Client("test_sender")

    client.connect(MQTT_ADDR, MQTT_PORT)
    client.publish("shem/ntfy/")

if __name__ == "__main__":
    main()

