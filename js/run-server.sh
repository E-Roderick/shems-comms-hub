#!/usr/bin/bash

# Load config variables
if [[ $__SHEMS_CONF -ne 1 ]]; then
	source ../config.sh;
fi

# Start the web API server and site server
node ./serve/server.js &
node ./site/dist/server.js

