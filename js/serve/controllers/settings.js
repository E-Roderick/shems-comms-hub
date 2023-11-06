import getDatabase from "../utils/db.js";

/*
 * Retrieve all rows from the `settings` table.
 */
export async function getAllSettings(req, res) {
	const db = getDatabase();
	const query = "SELECT * FROM settings"
	const settings = db.prepare(query).all()

	db.close();
	return res.json(settings);
}

/*
 * Retrieve a single row from the `settings` table.
 */
export async function getDeviceSettings(req, res) {
	const db = getDatabase();

    // Query values
    const deviceId = req.params.id;
    const defaultQuery = `
        SELECT *
        FROM settings
        WHERE dev_id = (?) AND is_default = 1
        ORDER BY code ASC
    `;
    const nonDefaultQuery = `
        SELECT *
        FROM settings
        WHERE dev_id = (?) AND is_default = 0
        ORDER BY code ASC
    `;

    const settings = [defaultQuery, nonDefaultQuery].map((q) => (
        db.prepare(q).all(deviceId)
    ));

	// Close database connection
	db.close();

	return res.json(settings);
}

