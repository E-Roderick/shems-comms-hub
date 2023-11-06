#!/bin/bash

##
# Place SHEMS operation environment variables here
#

export SHEMS_BASE_PATH='/shems'
export SHEMS_DB_PATH="$SHEMS_BASE_PATH/db.sqlite3"
export SHEMS_DATA_PATH="$SHEMS_BASE_PATH/data"
export SHEMS_LOG_PATH="$SHEMS_BASE_PATH/shems.log"

export MQTT_LOG_PATH="$SHEMS_BASE_PATH/mqtt_shems.log"
#export MQTT_LOG_PATH=$SHEMS_LOG_PATH	# Log all messages to single file
export MQTT_PORT=1883

export DISPATCH_SIZE=10
export DISPATCH_TIMEOUT=10
export DISPATCH_CYCLE=False

