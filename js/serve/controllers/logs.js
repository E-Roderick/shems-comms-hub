import { readFile } from "node:fs/promises";

const LOG_FILE_PATH = "/shems/shems.log"

/*
 * Retrieve log file contents.
 */
export async function getLogs(req, res) {
	const LINE_LIMIT = 250;

	try {
		const contents = await readFile(LOG_FILE_PATH, {encoding: 'utf-8'});
		return res.json(
			contents
				.split("\n")
				.slice(-LINE_LIMIT)
				.reverse()
		);
	} catch (err) {
		console.error(err);
		return res.json([""]);
	}
}

