"""
File: env_vars.py
Email: e.roderick@uqconnect.edu.au
Description: Exposure of OS environment variables as python vars. Defaults are
    defined per variable.
"""

import os

# Environment Variables
SHEMS_DEV = os.getenv('SHEMS_DEV', 'False') == 'True'
SHEMS_DB_PATH= os.getenv('SHEMS_DB_PATH', 'shems.sqlite3')
SHEMS_DATA_PATH = os.getenv('SHEMS_DATA_PATH', 'data')
SHEMS_LOG_PATH = os.getenv('SHEMS_LOG_PATH', 'shems.log')

MQTT_ADDR = os.getenv('MQTT_ADDR', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', '1883'))

DISPATCH_CYCLE = os.getenv('DISPATCH_CYCLE', 'False') == 'True'
DISPATCH_SIZE = int(os.getenv('DISPATCH_SIZE', '50'))
DISPATCH_TIMEOUT = float(os.getenv('DISPATCH_TIMEOUT', '5'))

