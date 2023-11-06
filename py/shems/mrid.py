import uuid

def get_device_mrid() -> uuid.UUID:
    """ Return a UUID mRID that is based on device address information, making
        the host identifiable.
    """
    return uuid.uuid3(uuid.NAMESPACE_URL, str(uuid.getnode()))

def get_random_mrid() -> uuid.UUID:
    """ Return a UUID mRID that is randomly generated. """
    return uuid.uuid4()

