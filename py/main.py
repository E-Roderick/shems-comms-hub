#!/bin/python
"""
File: main.py
Email: e.roderick@uqconnect.edu.au
Description: Entry-point for the SHEMS communication server.
"""
import logging

import uvicorn

from common.env_vars import SHEMS_DEV
from common.logging import log_config

# Setup logging according to schema
logging.config.dictConfig(log_config)

# Main program
def main():
    """ Start the SHEMS server and action dispatcher """
    if SHEMS_DEV:
        logging.debug("Starting SHEMS server in dev mode")

    # Configure uvicorn server
    config = uvicorn.Config(
        "server.server:shems_server",
        server_header=False,
        reload=SHEMS_DEV,           # Enable hot reload if developing
        log_config=log_config,
        host='0.0.0.0',             # Allow connections remotely and locally
    )
    server = uvicorn.Server(config)
    server.run()

if __name__ == "__main__":
    main()

