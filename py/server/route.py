from shems.uri import get_endpoint, UriType


def get_route(route_uri: UriType, template_value: str = '') -> str:
    # Create endpoint with template value as device ID and ensure it has
    # standard URI format
    endpoint = get_endpoint(route_uri, template_value)
    return f"/{endpoint}"

# App routes
ROOT = "/"
TEST = "/test/"

GET_ALARM = get_route(UriType.ALARM)
GET_DER = get_route(UriType.DER)
GET_DEVICES = get_route(UriType.DEVICE)
GET_DEVICE_INDEX = get_route(UriType.DEVICE, "{dev_index}")
GET_DEVICE_ID = get_route(UriType.DEVICE, "/id/{dev_id}")

POST_NOTIFY = get_route(UriType.NOTIFY)

