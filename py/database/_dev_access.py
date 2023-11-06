"""
File: _dev_access.py
Email: e.roderick@uqconnect.edu.au
Description: Developer access to the sqlite database object. Should only be used
    in state/end-of-lifetime events.
"""

import sqlite3 as sql

from common.env_vars import SHEMS_DB_PATH

# These tables should mirror the schema outlined in constants
TABLE_DEVICES = """devices(
    dev_id PRIMARY KEY,
    last_ip,
    description
)"""

# NOTE This may mean that a control_codes table is needed
TABLE_ALARMS = """alarms(
    dev_id NOT NULL,
    code NOT NULL,
    reading_time NOT NULL,
    value,
    PRIMARY KEY(dev_id, code, reading_time),
    FOREIGN KEY(dev_id) REFERENCES devices(dev_id)
)"""

TABLE_READINGS = """reading(
    reading_id PRIMARY KEY,
    dev_id NOT NULL,
    start_time NOT NULL,
    duration NOT NULL,
    description NOT NULL,
    readings NOT NULL,
    FOREIGN KEY(dev_id) REFERENCES devices(dev_id)
)"""

# This setup will store the most recent default and non-default versions of a
# code per device. NOTE May want to check.
TABLE_SETTINGS = """settings(
    dev_id NOT NULL,
    code NOT NULL,
    value NOT NULL,
    is_default NOT NULL,
    creation_time,
    start_time,
    duration,
    finish_time,
    PRIMARY KEY(dev_id, code, is_default),
    FOREIGN KEY(dev_id) REFERENCES devices(dev_id)
)"""

TABLE_STATUS = """status(
    dev_id PRIMARY KEY,
    reading_time NOT NULL,
    connect_status NOT NULL,
    charge_state,
    FOREIGN KEY(dev_id) REFERENCES devices(dev_id)
)"""

TABLES = [
    TABLE_DEVICES,
    TABLE_ALARMS,
    TABLE_READINGS,
    TABLE_SETTINGS,
    TABLE_STATUS,
]

def create_database():
    """ Create sqlite database according to above schema. """
    con = sql.connect(SHEMS_DB_PATH)
    cur = con.cursor()

    for table in TABLES:
        print(f"Creating table {table.partition('(')[0]}")
        cur.execute("CREATE TABLE IF NOT EXISTS " + table)

def destroy_database():
    """ Remove all tables from within the database """
    con = sql.connect(SHEMS_DB_PATH)
    cur = con.cursor()

    for table in TABLES[::-1]:
        print(f"Dropping table {table.partition('(')[0]}")
        cur.execute("DROP TABLE " + table.partition('(')[0])

