"""
File: database/constants.py
Email: e.roderick@uqconnect.edu.au
Description: Definitions of shems database schema related variables.
"""

from enum import Enum

# Enums
class Tables(Enum):
    """ Definitions of all table names """
    DEVICES = "devices"
    ALARMS = "alarms"
    READINGS = "readings"
    SETTINGS = "settings"
    STATUS = "status"

# Constants
SCHEMA = {
    Tables.DEVICES.value: {
        "dev_id": "dev_id",
        "last_ip": "last_ip",
        "description": "description"
    },
    Tables.ALARMS.value: {
        "dev_id": "dev_id",
        "code": "code",
        "reading_time": "reading_time",
        "value": "value"
    },
    Tables.READINGS.value: {
        "reading_id": "reading_id",
        "dev_id": "dev_id",
        "start_time": "start_time",
        "duration": "duration",
        "description": "description",
        "readings": "readings",
    },
    Tables.SETTINGS.value: {
        "dev_id": "dev_id",
        "code": "code",
        "update_time": "update_time",
        "value": "value",
    },
    Tables.STATUS.value: {
        "dev_id": "dev_id",
        "reading_time": "reading_time",
        "connect_status": "connect_status",
        "charge_state": "charge_state",
    },
}

DEVICE_STATUS_OFF = 0
DEVICE_STATUS_ON = 1

