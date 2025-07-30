from .core import (NotificationMsg,
                   InfoMsg,
                   ActivityMsg,
                   AlertMsg,
                   WarningMsg,
                   ErrorMsg,
                   CriticalMsg,
                   Priority,
                   broadcast,
                   broadcast_msg,
                   broadcast_alert_msg,
                   broadcast_info,
                   broadcast_activity,
                   broadcast_alert,
                   broadcast_warning,
                   broadcast_error,
                   broadcast_critical,
                   priority_of,
                   valid_priority)
from .instrumentation import Service, Periodic
import sys
from loguru import logger as log

# Logging Configuration
config = {
    "handlers": [
        {"sink": sys.stdout, "colorize": True, "level": "INFO",
         "format": "{time} | <level>{level} | {message}</level>"}
    ]
}
log.configure(**config)
# log.enable("robotnikmq") # uncomment for debug messages from robotnikmq

# Constants
SECONDS = 1
MINUTES = 60 * SECONDS
HOURS = 60 * MINUTES
DAYS = 24 * HOURS
WEEKS = 7 * DAYS
