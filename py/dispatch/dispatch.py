import logging
from typing import Any, Callable

from common.ring_buffer import NotifyBufferFinish, RingBuffer
from common.thread_control import ThreadCloser
from dispatch.actions import DISPATCH_ACTIONS, DispatchAction

# Functions
def _action_lookup(action: DispatchAction) -> Callable:
    return DISPATCH_ACTIONS[action]


# Dispatch Thread
def dispatcher_t(
    buffer: RingBuffer,
    closer: ThreadCloser,
) -> None:
    """ Thread to handle performing operations other than server requests. """
    logging.info("Starting dispatcher")
    while not closer.is_killed():
        # Wait until thread is active
        closer.wait()

        # Wait for an item to dispatch
        msg = buffer.get()

        # Check for thread shutdown
        if isinstance(msg, NotifyBufferFinish):
            buffer.confirm_sentinel(msg)
            break

        action, data = msg
        # Attempt to get the correct handler
        try:
            action_handler = _action_lookup(action)
            if action_handler is None:
                continue
        except ValueError as e:
            logging.warning("Invalid action given. %s", e)
            continue

        # Dispatch based on received message
        try:
            action_handler = log_handler(action_handler, data)
            if data:
                action_handler(data)
            else:
                action_handler()
        except Exception as e:
            # Want to ensure thread remains operational, so no errors should
            # be raised.
            logging.error(
                "Error in executing action '%s' with '%s'. %s",
                action, action_handler, e
            )
            continue

    # Thread closing - cleanup
    logging.info("Closing dispatcher")


def log_handler(func: Callable, data: Any) -> Callable:
    """ Wrap the given function with a helper to log the function result. """
    def wrapper(*args):
        logging.info("Performing '%s' with data '%s'", func.__name__, data)
        return func(*args)

    return wrapper

