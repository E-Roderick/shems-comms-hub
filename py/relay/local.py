"""
File: local.py
Email: e.roderick@uqconnect.edu.au
Description: Relay communication and information locally. I.e. to other
    processes on-device.
"""

from pathlib import Path

from common.env_vars import SHEMS_DATA_PATH

def writeout(code: str, value: str, keep: bool = True):
    """ Write the value of a code to a file named `code` in the SHEMS_DATA_PATH.
        If `keep`ing, the file will be appended, otherwise the file will be
        rewritten.

        If the file is being kept, a newline char ('\n') will be appended to the
        code value. Otherwise, the code will be written as-is.
    """
    mode = 'a' if keep else 'w'
    filepath = Path(SHEMS_DATA_PATH) / code

    with open(filepath, mode) as f:
        out = value + '\n' if keep else ''
        f.write(out)

