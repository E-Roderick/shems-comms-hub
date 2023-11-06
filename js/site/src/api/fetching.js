import { WEB_API_ADDR, WEB_API_PORT } from "../utils/env_var.js";

// Constants
const API_LOGS = `http://${WEB_API_ADDR}:${WEB_API_PORT}/api/logs`;
const API_ALARMS = `http://${WEB_API_ADDR}:${WEB_API_PORT}/api/alarms`;
const API_DEVICES = `http://${WEB_API_ADDR}:${WEB_API_PORT}/api/devices`;
const API_SETTINGS = `http://${WEB_API_ADDR}:${WEB_API_PORT}/api/settings`;
const API_STATUS = `http://${WEB_API_ADDR}:${WEB_API_PORT}/api/status`;

// Log files
const fetchLogs = async () => {
	console.log(import.meta.env)
    const resp = await fetch(API_LOGS);
    return resp.json();
}

// Table `alarms`
/*
 * Fetch the data for all alarms.
 */
const fetchAlarms = async () => {
    const resp = await fetch(API_ALARMS);
    return resp.json();
}

// Table `devices`
/*
 * Fetch the data for a single device.
 */
const fetchDevice = async id => {
    const resp = await fetch(`${API_DEVICES}/${id}`);
    return resp.json();
}

/*
 * Fetch the data for all devices.
 */
const fetchDevices = async () => {
    const resp = await fetch(API_DEVICES);
    return resp.json();
}

// Table `settings`
/*
 * Fetch the default settings for a single device.
 */
const fetchDeviceSettings = async id => {
    const resp = await fetch(`${API_SETTINGS}/${id}`);
    return resp.json();
}

// Table `status`
/*
 * Fetch the status of a single device.
 */
const fetchDeviceStatus = async id => {
    const resp = await fetch(`${API_STATUS}/${id}`);
    return resp.json();
}

export {
    fetchAlarms,
    fetchDevice,
    fetchDevices,
    fetchDeviceSettings,
    fetchDeviceStatus,
    fetchLogs,
};
