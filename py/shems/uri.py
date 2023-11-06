import ipaddress, sys
from enum import Enum

from common.connect import get_addresses


# Enums
class UriType(Enum):
    BASE = "BASE"
    FUNCTION = "FUNCTION"

    DER = "DER"
    DEVICE = "DEVICE"
    ALARM = "ALARM"
    NOTIFY = "NOTIFY"


# Constants
URI_BASE = "http://{}/"
URI_PATHS = {
    UriType.FUNCTION: {
        UriType.DER: "der/",
        UriType.DEVICE: "dev/{}/",
        UriType.ALARM: "alm/",
        UriType.NOTIFY: "ntfy/",
    },
}
DEVICE_ID_URI_SEG = "id/{}"

def get_endpoint(uri_type: UriType = UriType.BASE, dev_id: str = None) -> str:
    if uri_type == UriType.DEVICE and dev_id is None:
        raise ValueError(f"Uri type '{uri_type}' requires parameter 'dev_id'")

    endpoint = "shem/" + URI_PATHS.get(UriType.FUNCTION).get(uri_type)

    if uri_type == UriType.DEVICE:
        endpoint = endpoint.format(dev_id)
    return endpoint.replace("//", "/")

def get_uri(
    uri_type: UriType = UriType.BASE,
    ip_addr: str = None,
    dev_id: str = None,
) -> str:
    if ip_addr is None:
        # Store the first IP address from the devices networks
        ip_addr = get_addresses()[0][0]

    # Ensure required args are given
    if uri_type == UriType.DEVICE and dev_id is None:
        raise ValueError(f"Uri type '{uri_type}' requires parameter 'dev_id'")

    if uri_type == UriType.BASE:
        return URI_BASE.format(ip_addr)

    # Create specific URI
    blank_uri = URI_BASE + get_endpoint(uri_type, dev_id)

    if uri_type == UriType.DEVICE:
        return blank_uri.format(ip_addr)

    return blank_uri.format(ip_addr)

