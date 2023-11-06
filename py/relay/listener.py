"""
File: listener.py
Email: e.roderick@uqconnect.edu.au
Description: Functions related to the MQTT broker listener/subscriber, that
    handles in-network communication from devices.
"""
import logging

import paho.mqtt.client as mqtt

from common.env_vars import MQTT_ADDR, MQTT_PORT
from common.ring_buffer import RingBuffer
from common.thread_control import ThreadCloser
from dispatch.actions import buffer_dispatch, DispatchAction
from relay.remote import MQTT_TOPIC_ALARM, MQTT_TOPIC_DEVICE
from shems.mrid import get_device_mrid


# Constants
SENTINEL_TOPIC = "listener/sentinel"
TOPICS = [SENTINEL_TOPIC, MQTT_TOPIC_ALARM, MQTT_TOPIC_DEVICE]

MQTT_TIMEOUT = 1

DATA_DELIMITER = ','


# Listener Thread
def mqtt_listener_t(
    buffer: RingBuffer,
    closer: ThreadCloser,
) -> None:
    """ Thread to handle listening for and passing actions to the dispatcher
        from an MQTT broker.
    """
    logging.info("Starting MQTT listener")

    # Create MQTT client
    client_id = f"{get_device_mrid()}_listener" # Add to mRID for disambiguation
    client = mqtt.Client(client_id)
    client.on_connect = _on_connect
    client.on_message = _on_message

    # Fill client data values
    client.dispatch_buf = buffer

    # Set the client to active
    client.is_killed = False
    client.connect(MQTT_ADDR, MQTT_PORT)

    while not closer.is_killed():
        # Wait until thread is active
        closer.wait()

        # Check if listener should close
        if client.is_killed:
            break

        # Blocking loop
        client.loop(MQTT_TIMEOUT)

    # Thread closing - cleanup
    logging.info("Closing MQTT listener")


# Listener methods
def _on_connect(client: mqtt.Client, userdata, flags, ret_val: int):
    """ Callback for CONNACK response from broker. """
    logging.info("MQTT listener connected to broker with value %d", ret_val)

    # Subscribe to topics
    for topic in TOPICS:
        logging.info("MQTT listener subscribing to %s", topic)
        client.subscribe(topic)


def _on_message(client: mqtt.Client, userdata, msg):
    """ Callback for PUBLISH message received from broker. Of note in the
        received data is `msg.topic`, and the `msg.payload`, which is a byte
        string.
    """
    topic, data = msg.topic, msg.payload.decode()
    logging.info("Listener on topic '%s' received '%s'", topic, data)

    # Check if the listener should close
    if topic == SENTINEL_TOPIC:
        client.is_killed = True

    # Dispatch relevant action
    elif topic == MQTT_TOPIC_ALARM:
        dispatch_data = data.split(DATA_DELIMITER)
        buffer_dispatch(
            client.dispatch_buf,
            DispatchAction.LISTEN_RECV_ALARM,
            dispatch_data
        )

    elif topic == MQTT_TOPIC_DEVICE:
        dispatch_data = data.split(DATA_DELIMITER)
        buffer_dispatch(
            client.dispatch_buf,
            DispatchAction.LISTEN_RECV_DEV,
            dispatch_data
        )

