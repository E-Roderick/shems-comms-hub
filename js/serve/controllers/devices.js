import getDatabase from "../utils/db.js";

/*
 * Retrieve all rows from the `devices` table.
 */
export async function getAllDevices(req, res) {
	const db = getDatabase();
	const query = "SELECT * FROM devices"
	const devices = db.prepare(query).all()

	db.close();
	return res.json(devices);
}

/*
 * Retrieve a single row from the `devices` table.
 */
export async function getDevice(req, res) {
	const db = getDatabase();
    // Query values
    const deviceId = req.params.id;
    const query = "SELECT * FROM devices WHERE dev_id = (?)";
	const device = db.prepare(query).get(deviceId)

	db.close();
	return res.json(device);
}

