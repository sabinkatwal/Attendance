"""
Logging setup for Smart Attendance System.
Initializes both file and console logging.
"""

import logging
import os
from datetime import datetime
from config import LOG_DIR, LOG_LEVEL, LOG_FORMAT, LOG_FILE_NAME

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Create logger
logger = logging.getLogger("SmartAttendance")
logger.setLevel(logging.DEBUG)

# File handler
log_file_path = os.path.join(LOG_DIR, LOG_FILE_NAME)
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

# Formatter
formatter = logging.Formatter(LOG_FORMAT)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module."""
    return logging.getLogger(f"SmartAttendance.{name}")
