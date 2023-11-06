#!/bin/bash

# Operation flag
export SHEMS_OPERATE=1

# Connection for core shems device
export SHEMS_API_ADDR=localhost
export SHEMS_API_PORT=8000

# Connection for web API server
export WEB_API_ADDR=localhost
export WEB_API_PORT=8002

# Connection for website
export WEB_SITE_ADDR=localhost
export WEB_SITE_PORT=3000

# SHEMS paths 
export SHEMS_BASE_PATH='/shems'
export SHEMS_DB_PATH="$SHEMS_BASE_PATH/db.sqlite3"
export SHEMS_DATA_PATH="$SHEMS_BASE_PATH/data"
export SHEMS_CORE_PATH="$SHEMS_BASE_PATH/core"
export SHEMS_SITE_PATH="$SHEMS_BASE_PATH/website"

# Logging paths
export SHEMS_LOG_PATH="$SHEMS_BASE_PATH/shems.log"
export MQTT_LOG_PATH="$SHEMS_BASE_PATH/mqtt_shems.log"
# NOTE: Comment out next line to log to separate files
export MQTT_LOG_PATH=$SHEMS_LOG_PATH	# Log all messages to single file

# Configuration for MQTT broker
export SHEMS_BROKER=True	# Enable this device as the SHEMS MQTT broker
export MQTT_ADDR="0.0.0.0"	# NOTE: Need to manually copy to mosquitto.conf
export MQTT_PORT=1883		# NOTE: Need to manually copy to mosquitto.conf

# Dispatch queue/ring-buffer behaviour
export DISPATCH_SIZE=10
export DISPATCH_TIMEOUT=10
export DISPATCH_CYCLE=False


# DO NOT EDIT
export __SHEMS_CONF=1

