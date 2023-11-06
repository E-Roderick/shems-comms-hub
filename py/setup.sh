#!/bin/bash
# NOTE: This setup file is intended to run on a Raspberry Pi

# ErrNos
E_NOTROOT=87

# Require root
if ! $(sudo -l &> /dev/null); then
	echo "ERROR: root privileges are required for this script"
	exit $E_NOTROOT
fi

# Load SHEMS config values
source ./config.sh

# Create directories
mkdir -p $SHEMS_BASE_PATH && chmod 777 $SHEMS_BASE_PATH
mkdir -p $SHEMS_DATA_PATH && chmod 777 $SHEMS_DATA_PATH

# Install pre-reqs
apt-get update
apt-get install -y mosquitto

# Create python environment
SHEM_ENV_PATH="$SHEMS_BASE_PATH/shem-env"
python -m venv $SHEM_ENV_PATH

# Install python pre-reqs
source "$SHEM_ENV_PATH/bin/activate"
source ./config.sh
pip install -r ./requirements.txt

