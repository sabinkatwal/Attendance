"""
Auto Attendance System - Main attendance marking module.
Handles real-time face recognition and attendance marking.
"""

import cv2
import face_recognition
import pickle
import numpy as np
from datetime import datetime
import mysql.connector
import time
from typing import Tuple, Set, List
import config
from logging_setup import get_logger

logger = get_logger(__name__)

# ─────────────────────────────────────────────────────────────
# COLORS (BGR)
# ─────────────────────────────────────────────────────────────
GREEN  = (0, 210, 100)
RED    = (0, 70, 220)
YELLOW = (0, 200, 255)
WHITE  = (255, 255, 255)
DARK   = (20, 20, 30)
GREY   = (150, 150, 150)


# ─────────────────────────────────────────────────────────────
# MARK ATTENDANCE
# ─────────────────────────────────────────────────────────────
def mark_attendance(cursor, conn, identifier) -> Tuple[bool, str]:
    """
    Mark attendance using student_id (int) or name (str)
    Returns (success, message)
    """
    try:
        sid = None
        display_name = str(identifier)

        if isinstance(identifier, int):
            sid = identifier
            cursor.execute("SELECT name FROM students WHERE student_id=%s", (sid,))
            row = cursor.fetchone()
            if row:
                display_name = row[0]
        else:
            cursor.execute("SELECT student_id FROM students WHERE name=%s", (display_name,))
            row = cursor.fetchone()
            if not row:
                logger.warning(f"Student not found: {display_name}")
                return False, "Student not found"
            sid = row[0]

        now = datetime.now()
        today = now.date()
        current_time = now.time()

        cursor.execute(
            "SELECT id FROM attendance WHERE student_id=%s AND date=%s",
            (sid, today)
        )

        if cursor.fetchone():
            logger.debug(f"Duplicate attendance attempt: {display_name}")
            return False, "already_marked"

        cursor.execute(
            "INSERT INTO attendance (student_id, date, time, status) VALUES (%s,%s,%s,%s)",
            (sid, today, current_time, "Present")
        )
        conn.commit()

        time_str = current_time.strftime("%H:%M:%S")
        logger.info(f"✅ {display_name} marked at {time_str}")
        return True, time_str

    except Exception as e:
        logger.error(f"Error marking attendance for {identifier}: {e}")
        return False, str(e)


# ─────────────────────────────────────────────────────────────
# DRAW FACE BOX
# ─────────────────────────────────────────────────────────────
def draw_label_box(frame: np.ndarray, x1: int, y1: int, x2: int, y2: int,
                   name: str, confidence: int, status: str) -> None:

    if status == "marked":
        color = GREEN
    elif status == "duplicate":
        color = YELLOW
    else:
        color = RED

    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

    label = f"{name}  {confidence}%"
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)

    cv2.rectangle(frame, (x1, y1 - th - 10), (x1 + tw + 10, y1), color, -1)
    cv2.putText(frame, label, (x1 + 5, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, DARK, 2)


# ─────────────────────────────────────────────────────────────
# DRAW OVERLAY
# ─────────────────────────────────────────────────────────────
def draw_overlay(frame: np.ndarray, marked_today: Set[str],
                 total_known: int, fps: float) -> None:

    h, w = frame.shape[:2]

    cv2.rectangle(frame, (0, 0), (w, 40), DARK, -1)
    cv2.putText(frame, "SMART ATTENDANCE SYSTEM",
                (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (80, 180, 255), 2)

    time_str = datetime.now().strftime("%H:%M:%S")
    stats = f"Present: {len(marked_today)}/{total_known} | {time_str} | FPS: {fps:.0f}"

    (tw, _), _ = cv2.getTextSize(stats, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    cv2.putText(frame, stats, (w - tw - 10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, GREY, 1)

    cv2.rectangle(frame, (0, h - 30), (w, h), DARK, -1)
    cv2.putText(frame, "Press Q to quit",
                (10, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                GREY, 1)


# ─────────────────────────────────────────────────────────────
# MAIN FUNCTION
# ─────────────────────────────────────────────────────────────
def auto_attendance() -> None:

    marked_today: Set[str] = set()

    # ── Load encodings ─────────────────────────────────────
    try:
        with open(config.ENCODINGS_FILE, "rb") as f:
            data = pickle.load(f)

        if len(data) == 2:
            known_encodings, student_names = data
            student_ids = [None] * len(known_encodings)
        elif len(data) == 3:
            known_encodings, student_ids, student_names = data
        else:
            raise ValueError("Invalid encodings format")

        total_known = len(set(student_names))
        logger.info(f"Loaded {total_known} students.")

    except Exception as e:
        logger.error(f"Failed to load encodings: {e}")
        print("Error loading encodings.")
        return

    # ── Connect DB ─────────────────────────────────────────
    try:
        conn = mysql.connector.connect(**config.DB_CONFIG)
        cursor = conn.cursor()
        print("Database connected.")
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        print("Database error.")
        return

    # ── Camera Setup ───────────────────────────────────────
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)

    fps = 0
    fps_count = 0
    fps_timer = time.time()
    frame_num = 0
    face_data = []

    print("Attendance started. Press Q to quit.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            frame_num += 1
            fps_count += 1

            if time.time() - fps_timer >= 1:
                fps = fps_count
                fps_count = 0
                fps_timer = time.time()

            if frame_num % config.CAMERA_FPS_PROCESS_EVERY == 0:

                small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

                locations = face_recognition.face_locations(rgb, model="hog")
                encodings = face_recognition.face_encodings(rgb, locations)

                face_data = []

                for enc, loc in zip(encodings, locations):

                    distances = face_recognition.face_distance(known_encodings, enc)

                    name = "Unknown"
                    confidence = 0
                    status = "unknown"

                    if len(distances) > 0:
                        best_idx = np.argmin(distances)
                        best_dist = distances[best_idx]
                        confidence = int((1 - best_dist) * 100)

                        if confidence > config.CONFIDENCE_THRESHOLD:
                            display_name = student_names[best_idx]
                            sid = student_ids[best_idx]

                            name = display_name

                            if sid:
                                success, info = mark_attendance(cursor, conn, sid)
                            else:
                                success, info = mark_attendance(cursor, conn, display_name)

                            if success:
                                marked_today.add(display_name)
                                status = "marked"
                            elif info == "already_marked":
                                status = "duplicate"

                    top, right, bottom, left = loc
                    face_data.append(
                        (left*4, top*4, right*4, bottom*4,
                         name, confidence, status)
                    )

            display = frame.copy()

            for (x1, y1, x2, y2, name, confidence, status) in face_data:
                draw_label_box(display, x1, y1, x2, y2, name, confidence, status)

            draw_overlay(display, marked_today, total_known, fps)

            cv2.imshow("Smart Attendance", display)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        cursor.close()
        conn.close()

        print("\nSession Ended.")
        print("Students marked:", len(marked_today))


# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    auto_attendance()