import Database from 'better-sqlite3';

const DATABASE_PATH = '/shems/db.sqlite3'

function getDatabase() {
	const db = new Database(DATABASE_PATH, { fileMustExist: true });
	db.pragma('journal_mode = WAL');
	return db;
}

export default getDatabase;

