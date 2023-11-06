"""
File: remote.py
Email: e.roderick@uqconnect.edu.au
Description: Functions to relay information to other *remote* devices.
"""

from typing import Callable

from paho.mqtt import publish
import paho.mqtt.client as mqtt

from shems.mrid import get_device_mrid
from shems.uri import get_endpoint, UriType

# Constants
MQTT_TOPIC_ALARM = get_endpoint(UriType.ALARM)
MQTT_TOPIC_DEVICE = get_endpoint(UriType.DEVICE, '')
MQTT_TOPIC_NOTIFY = get_endpoint(UriType.NOTIFY)

def _get_mqtt_client(
    client_id: str,
    on_connect: Callable = None,
    on_message: Callable = None
) -> mqtt.Client:
    """ Create and return an MQTT client with the given ID. Takes two optional
        functions as additional parameters. `on_connect` is called when the
        client first connect, and `on_message` is called when the client
        receives a message from a topic it is subscribed to.

    on_connect params:
        (client: mqtt.client, userdata, flags, ret_val: int)

    on_message params:
        (client: mqtt.client, userdata, msg)
    """
    c = mqtt.Client(client_id)
    c.on_connect = on_connect
    c.on_message = on_message
    return c


def topic_from_control(control: str) -> str:
    """ Convert a control code into an MQTT topic. """
    return MQTT_TOPIC_NOTIFY + control


def publish_mqtt(
    topic: str,
    data: bytes,
    client_id: str = None,
    hostname: str = "localhost",
    port: int = 1883
):
    """ Publish a single message using mqtt """
    if client_id is None:
        client_id = str(get_device_mrid())

    publish.single(
        topic,
        payload=data,
        hostname=hostname,
        port=port,
        client_id=client_id
    )

