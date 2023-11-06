import logging

from common.env_vars import SHEMS_LOG_PATH

# Define logging configuration
log_config = {
    "version": 1,
    "formatters": {
        "default": {
            "format": '%(levelname)s - %(asctime)s - %(message)s',
        },
    },
    "handlers": {
        "file_handler": {
            "class": "logging.FileHandler",
            "filename": SHEMS_LOG_PATH,
            "formatter": "default",
        },
        "console_handler": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {
        "level": "NOTSET",
        "handlers": ["file_handler", "console_handler"],
    },
}

