"""
Configuration module for Smart Attendance System.
Loads settings from environment variables or defaults.
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ═══════════════════════════════════════════════════════════════
# DATABASE CONFIGURATION
# ═══════════════════════════════════════════════════════════════
DB_CONFIG: Dict[str, Any] = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "smart_attendance")
}

# ═══════════════════════════════════════════════════════════════
# FACE RECOGNITION CONFIGURATION
# ═══════════════════════════════════════════════════════════════
CONFIDENCE_THRESHOLD = int(os.getenv("CONFIDENCE_THRESHOLD", "70"))
FACE_RECOGNITION_MODEL = os.getenv("FACE_RECOGNITION_MODEL", "small")  # "small" or "large"
FACE_RECOGNITION_JITTERS = int(os.getenv("FACE_RECOGNITION_JITTERS", "1"))  # 1=fast, 5+=accurate
FACE_CASCADE_PATH = os.getenv("FACE_CASCADE_PATH", "haarcascade/haarcascade_frontalface_default.xml")

# ═══════════════════════════════════════════════════════════════
# FACE DETECTION CONFIGURATION
# ═══════════════════════════════════════════════════════════════
CASCADE_SCALE_FACTOR = float(os.getenv("CASCADE_SCALE_FACTOR", "1.1"))
CASCADE_MIN_NEIGHBORS = int(os.getenv("CASCADE_MIN_NEIGHBORS", "4"))
CASCADE_MIN_SIZE = int(os.getenv("CASCADE_MIN_SIZE", "60"))

# ═══════════════════════════════════════════════════════════════
# CAMERA CONFIGURATION
# ═══════════════════════════════════════════════════════════════
CAMERA_WIDTH = int(os.getenv("CAMERA_WIDTH", "640"))
CAMERA_HEIGHT = int(os.getenv("CAMERA_HEIGHT", "480"))
CAMERA_FPS_PROCESS_EVERY = int(os.getenv("CAMERA_FPS_PROCESS_EVERY", "2"))  # Process every Nth frame

# ═══════════════════════════════════════════════════════════════
# REGISTRATION CONFIGURATION
# ═══════════════════════════════════════════════════════════════
REGISTRATION_NUM_IMAGES = int(os.getenv("REGISTRATION_NUM_IMAGES", "40"))
REGISTRATION_NO_FACE_THRESHOLD = int(os.getenv("REGISTRATION_NO_FACE_THRESHOLD", "120"))

# ═══════════════════════════════════════════════════════════════
# FILE PATHS
# ═══════════════════════════════════════════════════════════════
DATASET_DIR = os.getenv("DATASET_DIR", "dataset")
ENCODINGS_FILE = os.getenv("ENCODINGS_FILE", "encodings.pkl")
ATTENDANCE_EXPORT_DIR = os.getenv("ATTENDANCE_EXPORT_DIR", "attendance")
LOG_DIR = os.getenv("LOG_DIR", "logs")

# ═══════════════════════════════════════════════════════════════
# UI CONFIGURATION
# ═══════════════════════════════════════════════════════════════
WINDOW_WIDTH = int(os.getenv("WINDOW_WIDTH", "1160"))
WINDOW_HEIGHT = int(os.getenv("WINDOW_HEIGHT", "720"))
BLINK_FREQUENCY = int(os.getenv("BLINK_FREQUENCY", "800"))  # milliseconds
CLOCK_UPDATE_INTERVAL = int(os.getenv("CLOCK_UPDATE_INTERVAL", "1000"))  # milliseconds

# Color Palette
BG = os.getenv("COLOR_BG", "#080b12")
BG2 = os.getenv("COLOR_BG2", "#0d1220")
BG3 = os.getenv("COLOR_BG3", "#111827")
BORDER = os.getenv("COLOR_BORDER", "#1e293b")
CYAN = os.getenv("COLOR_CYAN", "#00d4ff")
CYAN_DIM = os.getenv("COLOR_CYAN_DIM", "#0ea5c9")
GREEN = os.getenv("COLOR_GREEN", "#00ff9d")
GREEN_DIM = os.getenv("COLOR_GREEN_DIM", "#059669")
AMBER = os.getenv("COLOR_AMBER", "#ffb300")
RED = os.getenv("COLOR_RED", "#ff3b5c")
PURPLE = os.getenv("COLOR_PURPLE", "#8b5cf6")
TEXT = os.getenv("COLOR_TEXT", "#e2e8f0")
TEXT2 = os.getenv("COLOR_TEXT2", "#64748b")
TEXT3 = os.getenv("COLOR_TEXT3", "#94a3b8")
WHITE = os.getenv("COLOR_WHITE", "#ffffff")

# ═══════════════════════════════════════════════════════════════
# LOGGING CONFIGURATION
# ═══════════════════════════════════════════════════════════════
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
LOG_FILE_NAME = os.getenv("LOG_FILE_NAME", "smart_attendance.log")

# Behaviour flags
# If True, GUI will automatically rebuild face encodings after registering a new student
AUTO_UPDATE_MODEL_AFTER_REGISTER = os.getenv("AUTO_UPDATE_MODEL_AFTER_REGISTER", "true").lower() in ("1","true","yes")
# If True, when a student is re-detected the attendance time will be updated instead of ignoring
ALLOW_UPDATE_ON_REDETECT = os.getenv("ALLOW_UPDATE_ON_REDETECT", "false").lower() in ("1","true","yes")
