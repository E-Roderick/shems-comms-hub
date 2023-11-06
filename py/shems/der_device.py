from __future__ import annotations
from typing import TypeAlias
from lxml import etree as ET

from common.xml import ContainsXml, create_element, create_subelement


# Types
Timestamp: TypeAlias = int


# Classes
class Device(ContainsXml):
    _xml_tag = 'EndDevice'

    def __init__(
        self,
        href: str,
        description: str,
        change_time: Timestamp,
        enabled: int,
        charge_state: float = None,
        log_link: str = None
    ):
        """ Constructs a Default Control message object.

        Params:
            href: The URI/URL to access this resource at.
            description: A description of the device.
            change_time: The timestamp for the last update from this device.
            enabled: Truthian value indicating if the device is operational.
            charge_state: A float representing the charge state of the device.
            log_link: An optional URI to the log list for the device.
        """
        self._attribs = {"href": href}
        self._description = description
        self._change_time = change_time
        self._enabled = str(int(enabled))
        self._charge_state = charge_state
        self._log_link = log_link

        super().__init__(self._xml_tag, self._attribs)
        self._construct()

    def _construct(self):
        """ Populate the xml representation of this object with the appropriate
            XML children.
        """
        if self._log_link:
            self._change_time_elem = create_subelement(
                self._xml,
                'LogEventListLink',
                self._log_link
            )

        self._change_time_elem = create_subelement(
            self._xml,
            'changedTime',
            str(self._change_time)
        )

        self._enabled_elem = create_subelement(
            self._xml,
            'enabled',
            self._enabled
        )

        self._description_elem = create_subelement(
            self._xml,
            'description',
            self._description
        )

        if self._charge_state:
            self._charge_state_elem = create_subelement(
                self._xml,
                'chargeState',
                str(self._charge_state)
            )

    def get_values(self) -> dict:
        values = {
            **self._attribs,
            'changeTime': self._change_time,
            'enabled': self._enabled,
            'description': self._description,
        }

        if self._log_link:
            values += {'LogEventListLink': self._log_link}

        return values


class DeviceList(ContainsXml):
    _xml_tag = 'EndDeviceList'

    def __init__(
        self,
        href: str,
        devices: list[Device]
    ):
        self._all = self._results = str(len(devices))
        self._attribs = {
            'href': href,
            'all': self._all,
            'results': self._results,
        }
        self._devices = devices

        super().__init__(self._xml_tag, self._attribs)
        self._construct()

    def _construct(self):
        for device in self._devices:
            self._xml.append(device.xml())

def parse_device(dev_root: ET.Element):
    """ Reconstruct a DER device message based on a DER device xml element. """
    device_attrs = dev_root.attrib
    description = dev_root.xpath('description')[0].text
    change_time = dev_root.xpath('changedTime')[0].text
    # Keep `enabled` as string to save casting back and forth
    enabled = dev_root.xpath('enabled')[0].text

    log_link = dev_root.xpath('LogEventListLink')
    log_link = log_link[0].text if log_link else None

    return Device(
        device_attrs['href'],
        description,
        change_time,
        enabled,
        log_link=log_link
    )

