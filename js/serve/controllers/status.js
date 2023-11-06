import getDatabase from "../utils/db.js";

/*
 * Retrieve all rows from the `status` table.
 */
export async function getAllStatus(req, res) {
	const db = getDatabase();
	const query = "SELECT * FROM status"
	const statuses = db.prepare(query).all()

	db.close();
	return res.json(statuses);
}

/*
 * Retrieve a single row from the `status` table.
 */
export async function getDeviceStatus(req, res) {
	const db = getDatabase();
    // Query values
    const deviceId = req.params.id;
    const query = "SELECT * FROM status WHERE dev_id = (?)";
	const deviceStatus = db.prepare(query).get(deviceId)

	db.close();
	return res.json(deviceStatus);
}

