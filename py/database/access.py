import sqlite3 as sql

from common.env_vars import SHEMS_DB_PATH

def get_cursor() -> tuple[sql.Connection, sql.Cursor]:
    """ Get an sqlite db connection and a cursor to execute queries with.
        Returns from this function should be used for multiple queries (if
        needed) per calling function.
    """
    con = sql.connect(SHEMS_DB_PATH)
    cur = con.cursor()

    return con, cur

