import express from "express";
import cors from "cors";

import { getAllAlarms } from "./controllers/alarms.js";
import { getAllDevices, getDevice } from "./controllers/devices.js";
import { getAllSettings, getDeviceSettings } from "./controllers/settings.js";
import { getAllStatus, getDeviceStatus } from "./controllers/status.js";
import { getLogs } from "./controllers/logs.js";
import { WEB_API_PORT } from "./utils/env_var.js";

/* Constants */
const PORT = WEB_API_PORT;

/* App */
const app = express();

/* Middleware */
app.use(express.json());
app.use(cors())

/* Routes */
app.get("/", (req, res) => {
	res.send("Well, howdy!")
});

app.get("/api/alarms/", getAllAlarms);

app.get("/api/devices/", getAllDevices);
app.get("/api/devices/:id/", getDevice);

app.get("/api/settings", getAllSettings);
app.get("/api/settings/:id/", getDeviceSettings);

app.get("/api/status", getAllStatus);
app.get("/api/status/:id/", getDeviceStatus);

app.get("/api/logs/", getLogs);

// Start app
app.listen(PORT, () => {
	console.log(`App listening on port ${PORT}`)
})

