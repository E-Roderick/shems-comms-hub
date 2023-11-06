#!/bin/bash
# NOTE: This script should be called to setup a *remote* SHEMS device

USAGE="./install <user@shems-remote>"

# Ensure script is proved a remote target
if [[ $# -ne 1 ]]; then
	echo "$USAGE"
	exit 1
fi

TARGET_ADDR=$(echo $1 | cut -d'@' -f2)

# Prepare config values
source ./config.sh
export SHEMS_API_ADDR=$TARGET_ADDR
export WEB_API_ADDR=$TARGET_ADDR

# Build website for distribution
cd ./js && ./setup_site.sh && cd -

# Clean node_modules
cd ./js/serve && rm -rf node_modules && cd -
cd ./js/site && rm -rf node_modules && cd -

# Copy files to remote
ssh "$1" 'rm -rf ~/shems-src/'
scp -r "$(pwd)" "$1":shems-src

# Execute device setup
ssh "$1" 'cd ~/shems-src/ && sudo ./setup_this_device.sh'

