from fastapi import HTTPException, Response

from common.env_vars import SHEMS_DEV
from database.access import get_cursor
from shems.der_device import Device, DeviceList
from shems.mrid import get_device_mrid
from shems.uri import DEVICE_ID_URI_SEG, get_uri, UriType


# Classes
class SHEMSResponse(Response):
    """ Custom base response class that presets some values for IEEE 2030.5
        communication.
    """
    media_type = "application/xml" if SHEMS_DEV else "application/sep+xml"

    def render(self, content) -> bytes:
        if isinstance(content, bytes):
            return content
        if isinstance(content, str):
            return content.encode("utf-8")

        raise HTTPException(
            status_code=400,
            detail=f'Content type {type(content)} not supported'
        )


# Response handlers
def handle_read_device(index: int = None) -> str:
    """ Get and return the known devices from the database. If an index is
        specified, only return that device. The list should be ordered with the
        host device as index 0.

    Params:
        index: The index of the device to select.

    Raises:
        (HTTPException) if the index is greater than device list length.
    """
    response = ''

    con, _ = get_cursor()
    mrid = str(get_device_mrid())
    device_values = con.execute(
        """
            SELECT *
            FROM devices
            INNER JOIN status using (dev_id)
            ORDER BY CASE dev_id WHEN ? THEN 1 ELSE 2 END
        """, (mrid,)
    ).fetchall()

    if not device_values:
        return response

    # Want the entire devices list
    if index is None:
        def new_device(values):
            mrid, ip, description, time, enabled, charge = values
            href = get_uri(UriType.DEVICE, ip, DEVICE_ID_URI_SEG.format(mrid))
            return Device(href, description, time, enabled, charge)

        devices = [new_device(values) for values in device_values]
        href = get_uri(UriType.DEVICE, dev_id='')
        response = str(DeviceList(href, devices))

    # Want a specific device
    else:
        if index >= len(device_values):
            raise HTTPException(
                status_code = 400,
                detail = 'Index exceeds device list'
            )

        mrid, ip, description, time, enabled, charge = device_values[index]
        href = get_uri(UriType.DEVICE, ip, DEVICE_ID_URI_SEG.format(mrid))
        response = str(Device(href, description, time, enabled, charge))

    return response


def handle_read_device_id(dev_id: str) -> str:
    """ Get and return the info of a single device based on device ID.

    Params:
        dev_id: The mRID of the target device.

    Raises:
        (HTTPException) if the device is not found.
    """
    con, _ = get_cursor()
    values = con.execute(
        """
            SELECT *
            FROM devices
            INNER JOIN status using (dev_id)
            WHERE devices.dev_id = ?
        """, (dev_id,)
    ).fetchone()

    if not values:
        raise HTTPException(
            status_code = 404,
            detail = 'Device ID not known'
        )

    mrid, ip, description, time, enabled, charge = values
    href = get_uri(UriType.DEVICE, ip, DEVICE_ID_URI_SEG.format(mrid))
    device = Device(href, description, time, enabled, charge)
    return str(device)

