"""
File: server/server.py
Email: e.roderick@uqconnect.edu.au
Description: Defines the SHEMS server endpoints
"""

from contextlib import asynccontextmanager
import threading

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from common.env_vars import DISPATCH_SIZE, DISPATCH_CYCLE, SHEMS_DEV
from common.ring_buffer import RingBuffer
from common.thread_control import ThreadCloser, ThreadController
from dispatch.actions import buffer_dispatch, DispatchAction
from dispatch.dispatch import dispatcher_t
from relay.listener import mqtt_listener_t
from server.request import get_params, RequestMethod, validate_request
from server.request import validate_request_notify
from server.response import handle_read_device, handle_read_device_id
from server.response import SHEMSResponse
import server.route as routes


# Initalise fastapi server object
@asynccontextmanager
async def lifespan(app: FastAPI):
    """ SHEMS server should have access to a dispatch thread for its entire
        lifetime. The dispatch thread can be communicated with using a
        ring-buffer and controlled using a thread controller.
    """
    # Create dispatcher thread
    dispatch_buf = RingBuffer(DISPATCH_SIZE, DISPATCH_CYCLE)
    dispatch_closer = ThreadCloser()
    _dispatcher_t = threading.Thread(
        target=dispatcher_t,
        args=(dispatch_buf, dispatch_closer)
    )
    dispatch_controller = ThreadController(_dispatcher_t, dispatch_closer)

    # Create listener thread
    listener_closer = ThreadCloser()
    _listener_t = threading.Thread(
        target=mqtt_listener_t,
        args=(dispatch_buf, listener_closer)
    )
    listener_controller = ThreadController(_listener_t, listener_closer)

    # Make structures endpoint-accessible
    app.state.dispatch_buf = dispatch_buf
    app.state.dispatch_ctrl = dispatch_controller
    app.state.listener_ctrl = listener_controller

    # Start threads
    dispatch_controller.start()
    listener_controller.start()

    # Dispatch action to ensure DB exists
    buffer_dispatch(dispatch_buf, DispatchAction.DB_INIT)

    # Dispatch action to ensure host in DB
    buffer_dispatch(dispatch_buf, DispatchAction.PRELOAD)

    # Dispatch to remove old non-default controls
    buffer_dispatch(dispatch_buf, DispatchAction.CONTROL_CLEAN)

    yield

    # Shutdown
    dispatch_buf.notify_finish()
    dispatch_controller.finish()
    listener_controller.finish()

shems_server = FastAPI(lifespan = lifespan)
shems_server.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)



# Endpoints
@shems_server.get(routes.ROOT)
def read_root():
    """ Testing message to return on server root """
    return { "msg": "Well howdy!" }


# SHEMS endpoints
@shems_server.get(routes.GET_DEVICES, response_class=SHEMSResponse)
def read_devices():
    """ List all of the known devices for this controller. """
    return handle_read_device()


@shems_server.get(routes.GET_DEVICE_INDEX, response_class=SHEMSResponse)
def read_device_index(dev_index: int):
    """ List details of a specific known device by index.

    Params:
        dev_index (int): A path parameter that refers to the index of the
            desired device according to the results from the GET_DEVICES
            endpoint.

    Raises:
        (HTTPException) if the index is greater than the number of devices.
    """
    return handle_read_device(dev_index)


@shems_server.get(routes.GET_DEVICE_ID, response_class=SHEMSResponse)
def read_device_id(dev_id: str):
    """ List details of a specific known device by device mRID.

    Params:
        dev_id: The UUID that identifies the device.

    Raises:
        (HTTPException) If the dev_id is not found within the db.
    """
    return handle_read_device_id(dev_id)


@shems_server.post(routes.POST_NOTIFY)
async def read_notify(request: Request):
    """ Handle incoming notification requests. This endpoint should be used to
        inform the SHEMS and its devices of changes.
    """
    headers, data = await validate_request(request, RequestMethod.POST)
    control = validate_request_notify(data)
    buffer_dispatch(
        request.app.state.dispatch_buf,
        DispatchAction.CONTROL,
        # Pass the control details and a buffer reference for future callbacks
        (control, request.app.state.dispatch_buf)
    )


# Developer endpoints
if SHEMS_DEV:
    @shems_server.get(routes.TEST, response_class=SHEMSResponse)
    def read_test(request: Request):
        """ Testing endpoint """
        print(get_params(str(request.query_params)))
        return "<msg>Testing</msg>"

