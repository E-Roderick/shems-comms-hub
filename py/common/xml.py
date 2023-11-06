from lxml import etree as ET

from common.env_vars import SHEMS_DEV

def create_element(tag: str, text: str = "", attrs: dict = {}) -> ET.Element:
    """ Construct an lxml etree element.

    Params:
        tag (str): The name of the xml element
        text (str): The text within the xml element
        attrs (dict[str, str]): The attributes to assign to the xml element

    Returns:
        (lxml.etree.Element)
    """
    element = ET.Element(tag, attrib=attrs)
    if text: element.text = text
    return element


def create_subelement(
    parent: ET.Element,
    tag: str,
    text: str = "",
    attrs: dict = {}
) -> ET.Element:
    """ Construct an lxml etree element with a parent.

    Params:
        parent (lxml.etree.Element): The parent element for the new xml element
        tag (str): The name of the xml element
        text (str): The text within the xml element
        attrs (dict[str, str]): The attributes to assign to the xml element

    Returns:
        (lxml.etree.Element)
    """
    element = create_element(tag, text, attrs)
    parent.append(element)
    return element


# Classes
class ContainsXml:
    """ A class to represent information that has an XML representation. """
    _pp = SHEMS_DEV # For debugging purposes. Enables pretty print for XML.

    def __init__(self, tag, attribs = {}):
        self._xml = ET.Element(tag, attrib = attribs)


    def xml(self) -> ET.Element:
        """ Get the XML representation of this object. """
        return self._xml


    def __repr__(self) -> str:
        return ET.tostring(self._xml, pretty_print=self._pp).decode()


    def __str__(self) -> str:
        return repr(self)

