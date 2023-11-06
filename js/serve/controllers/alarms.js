import getDatabase from "../utils/db.js";

/*
 * Retrieve all rows from the `alarms` table.
 */
export async function getAllAlarms(req, res) {
	const db = getDatabase();
	const query = "SELECT * FROM alarms"
	const alarms = db.prepare(query).all()

	db.close();
	return res.json(alarms);
}

