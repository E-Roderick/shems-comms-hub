#!/bin/bash
# NOTE: This setup file is intended to run on a Raspberry Pi

# ErrNos
E_NOTROOT=87

# Require root
if ! [ $(id -u) = 0 ]; then
	echo "ERROR: root privileges are required for this script"
	exit $E_NOTROOT
fi


###
# GENERAL SETUP
###
echo "~~~ SHEMS SETUP STEP 1: General Setup"

# Load SHEMS config values
source ./config.sh

# Wipe previous install
rm -rf config$SHEMS_BASE_PATH

# Create directories
mkdir -p $SHEMS_BASE_PATH && chmod 777 $SHEMS_BASE_PATH
mkdir -p $SHEMS_DATA_PATH && chmod 777 $SHEMS_DATA_PATH

# Copy config values
cp ./config.sh "$SHEMS_BASE_PATH"

# Install pre-reqs
apt-get update
apt-get install -y libxslt-dev mosquitto nodejs npm python3 python3-pip python3.11-venv

# Remove services
systemctl disable mosquitto.service


###
# SHEMS CORE SETUP
###
echo "~~~ SHEMS SETUP STEP 2: SHEMS Core Setup"

# Setup folder
cp -r ./py/ "$SHEMS_CORE_PATH"
chmod 777 "$SHEMS_CORE_PATH"

# Create python environment
SHEM_ENV_PATH="$SHEMS_CORE_PATH/shem-env"
python -m venv $SHEM_ENV_PATH

# Install python pre-reqs
source "$SHEM_ENV_PATH/bin/activate"
source ./config.sh
pip install -r "$SHEMS_CORE_PATH/requirements.txt"


###
# SHEMS WEBSITE SETUP
###
echo "~~~ SHEMS SETUP STEP 3: SHEMS Website Setup"

# Setup folders
SHEMS_SITE_WEB_PATH="$SHEMS_SITE_PATH/site/"

mkdir -p "$SHEMS_SITE_PATH" && chmod 777 "$SHEMS_SITE_PATH"
mkdir -p "$SHEMS_SITE_WEB_PATH"

cp ./js/*.sh "$SHEMS_SITE_PATH"
cp -r ./js/serve "$SHEMS_SITE_PATH"
cp -r ./js/site/dist "$SHEMS_SITE_WEB_PATH"
cp -r ./js/site/package.json "$SHEMS_SITE_WEB_PATH"

# Run website server setup
cd "$SHEMS_SITE_PATH" && ./setup_serve.sh
cd -


###
# ENABLE OPERATION SERVICE
###
echo "~~~ SHEMS SETUP STEP 4: Create Service"

# Create operating script
export SHEMS_RUN_SCRIPT="$SHEMS_BASE_PATH/run-all.sh"

cat > "$SHEMS_RUN_SCRIPT" <<EOF
#!/bin/bash

cd "$SHEMS_BASE_PATH"

source "$SHEMS_BASE_PATH/config.sh"

if [[ \$SHEMS_OPERATE -eq 1 ]]; then
	
	cd "\$SHEMS_CORE_PATH"
	source "$SHEM_ENV_PATH/bin/activate"
	./run-server.sh & 
	cd -
	
	cd "\$SHEMS_SITE_PATH"
	./run-server.sh # Do not want to detach all servers
	cd -
fi
EOF

chmod 777 "$SHEMS_RUN_SCRIPT"

# Start SHEMS on boot
cat > "/etc/systemd/system/shems.service" <<EOF

[Unit]
Description=SHEMS

[Service]
ExecStart=$SHEMS_RUN_SCRIPT
Environment="PATH=\$PATH:$SHEM_ENV_PATH/bin"
WorkingDirectory=/shems/
Restart=on-failure
User=root

[Install]
WantedBy=multi-user.target
EOF

systemctl enable shems.service
systemctl start shems.service

echo "~~~ Installation (hopefully) Complete"

