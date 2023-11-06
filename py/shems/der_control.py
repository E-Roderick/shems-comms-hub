from __future__ import annotations
from typing import NamedTuple, TypeAlias
from lxml import etree as ET

from common.xml import ContainsXml, create_element, create_subelement


# Types
Timestamp: TypeAlias = int

class Interval(NamedTuple):
    duration: int
    start: Timestamp

class EventStatus(NamedTuple):
    currentStatus: int
    dateTime: Timestamp
    potentiallySuperceded: bool

class ControlValue(NamedTuple):
    control: str
    value: str

CurveControlValue: TypeAlias = ControlValue


# Classes
class DefaultControl(ContainsXml):
    """ A DER Control message that does not have associated timing. i.e. the
        control that should be in place when no time-specific controls are
        valid.
    """
    _xml_tag = 'DefaultDERControl'

    def __init__(
        self,
        href: str,
        reply_to: str,
        responses: int,
        mrid: str,
        description: str,
        controls: tuple[list[ControlValue], list[CurveControlValue]],
    ):
        """ Constructs a Default Control message object.

        Params:
            href: The URI/URL to access this resource at.
            reply_to: The URI/URL that should be used to respond to for
                regarding the originator of this message.
            responses: The number of expected responses to this message.
            mrid: A resource identifier
            description: A textual description of the control message.
            controls: A list of control values (a single value control) and a
                list of curve control values (x,y function control).
        """
        self._attribs = {
            "href": href,
            "replyTo": reply_to,
            "responsesRequired": str(responses),
        }

        self._mrid = mrid
        self._description = description
        self._controls = controls

        super().__init__(self._xml_tag, self._attribs)
        self._construct()


    def _construct(self):
        """ Populate the xml representation of this object with the appropriate
            XML children.
        """
        self._mrid_elem = create_subelement(self._xml, 'mRID', self._mrid)
        self._description_elem = create_subelement(
            self._xml,
            'description',
            self._description
        )

        self._base = ET.SubElement(self._xml, 'DERControlBase')
        for control in self._controls[0]:
            # Controls
            create_subelement(self._base, control.control, control.value)

        for control in self._controls[1]:
            # Curve controls
            ET.SubElement(
                self._base,
                control.control,
                attrib={'href': control.value}
            )


    def get_values(self) -> dict:
        return {
            **self._attribs,
            'mRID': self._mrid,
            'description': self._description,
            'controls': self._controls,
        }


class Control(DefaultControl):
    """ A DER Control message that will be in effect for a certain duration.
    """
    _xml_tag = 'DERControl'

    def __init__(
        self,
        href: str,
        reply_to: str,
        responses: int,
        mrid: str,
        description: str,
        creation_time: int,
        interval: Interval,
        status: EventStatus,
        controls: tuple[list[ControlValue], list[CurveControlValue]],
    ):
        """ Constructs a Control message object.

        Params:
            href: The URI/URL to access this resource at.
            reply_to: The URI/URL that should be used to respond to for
                regarding the originator of this message.
            responses: The number of expected responses to this message.
            mrid: A resource identifier
            description: A textual description of the control message.
            creation_time: The time that this Control message was created.
            interval: Information for the control's interval. This contains the
                duration of the control (seconds) and a timestamp for the start
                of the control.
            status: Information for the control's event status. Contains a
                status value as an enumerated int, a timestamp for when the
                status value was seet, and a bool to indicate if the status
                might (potentially) be superceded.
            controls: A list of control values (a single value control) and a
                list of curve control values (x,y function control).
        """
        self._description = description
        self._creation_time = str(creation_time)
        self._interval = interval
        self._status = status
        super().__init__(href, reply_to, responses, mrid, description, controls)


    def _construct(self):
        super()._construct()

        create_subelement(self._xml, 'creationTime', self._creation_time)

        interval = ET.SubElement(self._xml, 'interval')
        create_subelement(interval, 'duration', str(self._interval.duration))
        create_subelement(interval, 'start', str(self._interval.start))

        status = ET.SubElement(self._xml, 'EventStatus')
        create_subelement(status, 'currentStatus',
                          str(self._status.currentStatus))
        create_subelement(status, 'dateTime', str(self._status.dateTime))
        create_subelement(status, 'potentiallySuperceded',
                          str(self._status.potentiallySuperceded).lower())

        # Ensure control values are last item
        self._xml.remove(self._base)
        self._xml.append(self._base)


    def get_values(self):
        return {
            **super().get_values(),
            'creationTime': self._creation_time,
            'interval': self._interval,
            'EventStatus': self._status,
        }


def _parse_control_base(
    ctrl_base_root: ET.Element
) -> tuple[list[ControlValue], list[CurveControlValue]]:
    """ Reconstruct control values from a DERControlBase xml element """
    controls = []
    curve_controls = []

    for child in ctrl_base_root:
        if child.attrib:
            curve_controls.append(
                CurveControlValue(child.tag, child.attrib['href'])
            )
        else:
            controls.append(ControlValue(child.tag, child.text))

    return (controls, curve_controls)


def _parse_control_interval(interval_root: ET.Element) -> Interval:
    """ Reconstruct DER interval values from an interval xml element """
    duration = interval_root.xpath('duration')[0].text
    start = interval_root.xpath('start')[0].text
    return Interval(int(duration), int(start))


def _parse_control_status(status_root: ET.Element) -> EventStatus:
    """ Reconstruct DER event status  values from an EventStatus xml element """
    status = status_root.xpath('currentStatus')[0].text
    date = status_root.xpath('dateTime')[0].text
    superceded = status_root.xpath('potentiallySuperceded')[0].text
    return EventStatus(
        int(status),
        int(date),
        superceded == 'true'
    )


def parse_control(ctrl_root: ET.Element):
    """ Reconstruct a DER Control message (default or not) based on a DERControl
        or DERDefaultControl xml element.
    """
    # Get DER Control element's attributes
    control_attrs = ctrl_root.attrib

    # Get children common to all control types
    mrid = ctrl_root.xpath('mRID')[0].text
    description = ctrl_root.xpath('description')[0].text

    # Get control values
    control_values = _parse_control_base(ctrl_root.xpath('DERControlBase')[0])

    # Return early if default control
    if ctrl_root.tag == 'DefaultDERControl':
        return DefaultControl(
            control_attrs['href'],
            control_attrs['replyTo'],
            control_attrs['responsesRequired'],
            mrid,
            description,
            control_values
        )

    # Get remaining values
    creation_time = ctrl_root.xpath('creationTime')[0].text
    interval = _parse_control_interval(ctrl_root.xpath('interval')[0])
    status = _parse_control_status(ctrl_root.xpath('EventStatus')[0])

    return Control(
        control_attrs['href'],
        control_attrs['replyTo'],
        control_attrs['responsesRequired'],
        mrid,
        description,
        creation_time,
        interval,
        status,
        control_values
    )
