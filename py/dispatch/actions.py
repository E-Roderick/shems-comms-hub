import logging
import os
import time
from enum import Enum
from queue import Full
from threading import Timer
from typing import Any, Callable, NamedTuple

from common.connect import get_addresses
from common.env_vars import SHEMS_DB_PATH
from common.ring_buffer import Closed, RingBuffer
from database._dev_access import create_database
from database.constants import DEVICE_STATUS_OFF, DEVICE_STATUS_ON
from relay.local import writeout
from relay.remote import topic_from_control, publish_mqtt
from shems.der_control import Control, DefaultControl
from shems.mrid import get_device_mrid
import database.access as db

# Enums
class DispatchAction(Enum):
    """ The actions that the dispatcher can handle. """
    DB_INIT = "DB_Init"
    PRELOAD = "Preload"
    CONTROL = "DERControl"
    CONTROL_CLEAN = "DERControl_remove_old"
    CONTROL_EXPIRE = "auto_DERControl_default"
    LISTEN_RECV_DEV = "Listener_receive_device"
    LISTEN_RECV_ALARM = "Listener_receive_alarm"


# Classes
class DispatchData(NamedTuple):
    """ Container for a dispatchable action and the data the action needs. """
    action: DispatchAction
    data: Any


# Functions
def buffer_dispatch(
    buf: RingBuffer,
    action: DispatchAction,
    data: any = None,
    block: bool = True,
    timeout: float = None,
) -> bool:
    """ Dispatch an action to the dispatcher thread.

    Params:
        buf: The buffer/queue with which to send a message to the dispatcher
            thread.
        action: The action the dispatcher should undertake.
        data: Any information the specified action needs to take.
        block: Block on attempting to dispatch an action.
        timeout: If blocking, the time to wait for the buffer to unblock.

    Returns:
        False if the action was not dispatched due to the buffer being closed or
            full. True otherwise.
    """
    msg = DispatchData(action, data)
    success = True

    try:
        buf.put(msg, block, timeout)
    except (Closed, Full) as e:
        logging.warning("Could not place on buffer. %s", e)
        success = False
    return success


# Dispatch action handlers
def init_db():
    """ Create an sqlite3 database if one does not exist. """
    if not os.path.exists(SHEMS_DB_PATH):
        create_database()


def preload_host():
    """ Ensure that the host running the SHEMS server is present in the SHEMS
        device table.
    """
    mrid = get_device_mrid()
    address = str(get_addresses()[0][0])

    con, cur = db.get_cursor()
    res = cur.execute("SELECT * FROM devices WHERE dev_id = ?", (str(mrid),))

    # Make the host device known
    if res.fetchall():
        query = "UPDATE devices SET last_ip = ? WHERE dev_id = ?"
        cur.execute(query, (address, str(mrid)))
    else:
        query = """INSERT INTO devices (dev_id, last_ip, description)
            VALUES (?,?,?)"""
        cur.execute(query, (str(mrid), address, "SHEMS Host controller"))

    # Update device status
    query = """
        INSERT OR REPLACE INTO status(dev_id, reading_time, connect_status)
        VALUES (?, ?, ?)
    """
    cur.execute(query, (str(mrid), int(time.time()), DEVICE_STATUS_ON))
    con.commit()


def handle_clean_controls():
    """ Remove non-default controls that have expired. Intended to clean the
        database if the system has been offline for some time.
    """
    con, cur = db.get_cursor()
    query = """
        DELETE FROM settings
        WHERE finish_time <= ? AND is_default = False
    """
    current_time = time.time()

    cur.execute(query, (current_time,))
    con.commit()


def handle_control_msg(handler_data: tuple[DefaultControl, RingBuffer]):
    """ Update the control settings for a DER device in the database.
        TODO: Also inform the DER device via comms.

    Params:
        control: The control object to adjust settings with.
    """
    sent_control, dispatch_buf = handler_data
    con, cur = db.get_cursor()

    # Find valid device IDs
    devices = cur.execute("SELECT dev_id FROM devices").fetchall()
    devices = [mrid[0] for mrid in devices] # Unpack values from tuples

    control_values = sent_control.get_values()
    controls, _ = control_values['controls'] # TODO handle curve controls
    is_default = not isinstance(sent_control, Control)
    mrid = control_values['mRID']

    # Fail silently if referencing a bad device
    if mrid not in devices:
        logging.warning("Got control for unknown device")
        return

    # Initialise timing values
    creation = start = duration = finish = None
    if not is_default:
        creation = control_values['creationTime']
        duration, start = control_values['interval']
        finish = start + duration

    # Store the control value in database
    for control, value in controls:
        query = """
            INSERT INTO settings (
                dev_id, code, value, is_default, creation_time, start_time,
                duration, finish_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (dev_id, code, is_default) DO UPDATE SET
                value = excluded.value,
                creation_time = excluded.creation_time,
                start_time = excluded.start_time,
                duration = excluded.duration,
                finish_time = excluded.finish_time
        """
        cur.execute(query, (
            mrid, control, value, is_default, creation, start,
            duration, finish
        ))

        # Schedule removal of control behaviour if needed
        if not is_default:
            Timer(
                finish - time.time(),
                buffer_dispatch,
                [dispatch_buf, DispatchAction.CONTROL_EXPIRE, (mrid, control)]
            ).start()
    con.commit()

    # Relay the control information
    for control, value in controls:
        # Locally
        try:
            writeout(control, value)
        except OSError as e:
            logging.error("Error in relaying information locally. %s", e)
        # Remotely
        try:
            print(topic_from_control(control))
            publish_mqtt(topic_from_control(control), value)
        except OSError as e:
            logging.error("Error in relaying information remotely. %s", e)


def handle_control_revert(control_data: tuple[str]):
    """ Remove a non-default control from the control settings table.
        TODO also inform the device of the change.

    Params:
        control_data: The mRID and control code to be removed.
    """
    con, cur = db.get_cursor()
    query = """
        DELETE FROM settings
        WHERE dev_id = ? AND code = ? AND is_default = False
    """
    cur.execute(query, control_data)
    con.commit()


def handle_listener_dev(dev_data: tuple[str]):
    """ Update the status of a device based on a listener's received message.
        This will update the device and status tables.
    """
    mrid, last_ip, description, read_time, *dev_data = dev_data
    charge_state = None
    if dev_data:
        [charge_state] = dev_data
        charge_state = float(charge_state)

    con, cur = db.get_cursor()

    # Update device
    query = """
        INSERT OR REPLACE INTO devices(dev_id, last_ip, description)
        VALUES (?, ?, ?)
    """
    cur.execute(query, (mrid, last_ip, description))

    # Update device status
    query = """
        INSERT OR REPLACE INTO status(
            dev_id, reading_time, connect_status, charge_state
        )
        VALUES (?, ?, ?, ?)
    """
    cur.execute(query, (mrid, float(read_time), DEVICE_STATUS_ON, charge_state))
    con.commit()


def handle_listener_alarm(alarm_data: tuple[str]):
    """ Store the occurrence of a device alarm. This will update the status
        table as well as the alarm table.

        NOTE: In future, additional actions can be placed after the table
        updates to handle the alarm outcomes.
    """
    mrid, code, read_time, value, *alarm_data = alarm_data
    charge_state = None
    if alarm_data:
        [charge_state] = alarm_data
        charge_state = float(charge_state)

    con, cur = db.get_cursor()

    # Ensure device is known
    res = cur.execute("SELECT * FROM devices WHERE dev_id = ?", (str(mrid),))
    if not res.fetchall():
        logging.warning("Got alarm for unknown device '%e'", mrid)
        return

    # Update device status
    query = """
        INSERT OR REPLACE INTO status(
            dev_id, reading_time, connect_status, charge_state
        )
        VALUES (?, ?, ?, ?)
    """
    cur.execute(query, (mrid, float(read_time), DEVICE_STATUS_ON, charge_state))

    # Add alarm
    query = """
        INSERT INTO alarms(dev_id, code, reading_time, value)
        VALUES (?, ?, ?, ?)
    """
    cur.execute(query, (mrid, code, float(read_time), value))
    con.commit()


# Action to handler mapping
DISPATCH_ACTIONS: dict[DispatchAction, Callable] = {
    DispatchAction.CONTROL: handle_control_msg,
    DispatchAction.CONTROL_CLEAN: handle_clean_controls,
    DispatchAction.CONTROL_EXPIRE: handle_control_revert,
    DispatchAction.LISTEN_RECV_DEV: handle_listener_dev,
    DispatchAction.LISTEN_RECV_ALARM: handle_listener_alarm,
    DispatchAction.DB_INIT: init_db,
    DispatchAction.PRELOAD: preload_host,
}

