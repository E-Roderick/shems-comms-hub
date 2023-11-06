#!/usr/bin/bash

# Load config variables
if [[ $__SHEMS_CONF -ne 1 ]]; then
	source ../config.sh;
fi

# Check if host variable is defined
case $SHEMS_BROKER in
	True)
		echo "Running as SHEMS host" ;;
	False)
		echo "Running as SHEMS client" ;;
	*)
		echo "ERROR: Environment variable 'SHEMS_BROKER' not set"
		exit 1
		;;
esac

# If running as SHEMS host, start MQTT broker
if [[ $SHEMS_BROKER == True ]]; then
	( mosquitto -c ./mosquitto.conf 2>&1 | tee -a "$MQTT_LOG_PATH" ) &
fi

# Start the SHEMS fastapi server
python ./main.py

