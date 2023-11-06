import logging
from enum import Enum

from fastapi import HTTPException, Request
from lxml import etree as ET

from shems.der_control import parse_control

# Constants
VALID_CONTENT_TYPE = ('application/xml', 'application/sep+xml')

class RequestMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"


# Helpers
def get_params(query_params: str) -> dict[str, str]:
    """ Custom query parameter getter that follows the IEEE 2030.5 requirement
        of query parameters being ignored after the first instance, when read
        left to right.
    """
    result = {}
    params = [tuple(param.split('=')) for param in query_params.split('&')]

    for key, value in params:
        if key in result:
            continue

        result[key] = value

    return result


# Validation
async def validate_request(
    request: Request,
    method: RequestMethod
) -> tuple[dict, ET.Element]:
    """ Check that an incoming request is valid. A request is valid if it has
        the correct request method, the headers indicate the data body is xml,
        and the data body is valid XML.

    Raises:
        HTTPException: If any of the above conditions are not met.
    """
    if request.method != method.value:
        raise HTTPException(
            status_code = 405,
            headers = { 'Accept': RequestMethod.POST.value }
        )

    headers = request.headers
    if headers.get('content-type', None) not in VALID_CONTENT_TYPE:
        raise HTTPException(
            status_code = 415,
            detail = 'Incorrect content type',
            headers = { 'Accept': 'application/sep+xml,application/xml' }
        )

    try:
        data = await request.body()
        data_root = ET.fromstring(data)
    except Exception as e:
        # TODO: Make more specific exception catch
        logging.warning("Invalid request body. Err: %s", e)
        raise HTTPException(
            status_code = 400,
            detail = 'XML body could not be parsed'
        ) from e

    return headers, data_root


def validate_request_notify(data_root: ET.Element):
    """ Check that an incoming notify request is valid. A notify request is
        valid if its XML contains A DER Control message.

    Raises:
        HTTPException: If the XML does not contain a DER Control message, or if
        the message is malformed.
    """
    # Try to identify the received message
    try:
        if 'Control' in data_root.tag:
            control = parse_control(data_root)
            # Dispatch control event
        else:
            raise ValueError("Given XML does not contain a DER Control message")
    except Exception as e:
        # TODO: Make more specific exception catch
        logging.warning("Invalid request body. Err: %s", e)
        raise HTTPException(
                status_code = 400,
                detail = 'Invalid notification body'
        ) from e

    return control

