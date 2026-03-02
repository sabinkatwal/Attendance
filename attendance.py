"""
Attendance marking system - Real-time face recognition with high FPS (50 FPS target).
Optimized for Windows with cv2.CAP_DSHOW and efficient frame processing.
"""

import cv2
import face_recognition
import pickle
import numpy as np
from datetime import datetime
import mysql.connector
import os

# Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "1234",
    "database": "smart_attendance"
}

ENCODINGS_FILE = "encodings.pkl"
TOLERANCE = 0.6  # Face recognition tolerance (lower = stricter)
FRAME_SKIP = 2  # Process every Nth frame (helps with FPS)

# Colors (BGR)
GREEN = (0, 210, 100)
RED = (0, 70, 220)
YELLOW = (0, 200, 255)
WHITE = (255, 255, 255)
DARK = (20, 20, 30)


def load_encodings():
    """Load face encodings from pickle file"""
    if not os.path.exists(ENCODINGS_FILE):
        print(f"❌ {ENCODINGS_FILE} not found.")
        print("   Run: python face_encoding.py")
        return None, None, None
    
    try:
        with open(ENCODINGS_FILE, "rb") as f:
            data = pickle.load(f)
            if isinstance(data, tuple) and len(data) == 3:
                known_encodings, student_ids, student_names = data
                print(f"✓ Loaded {len(set(student_ids))} students ({len(known_encodings)} encodings)")
                return known_encodings, student_ids, student_names
            else:
                print(f"❌ Invalid encodings format")
                return None, None, None
    except Exception as e:
        print(f"❌ Error loading encodings: {e}")
        return None, None, None


def get_db_connection():
    """Create database connection"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        print(f"❌ Database error: {e}")
        return None


def is_already_marked(cursor, student_id, today_date):
    """Check if student already marked attendance today"""
    try:
        cursor.execute(
            "SELECT id FROM attendance WHERE student_id=%s AND date=%s",
            (student_id, today_date)
        )
        return cursor.fetchone() is not None
    except:
        return False


def mark_attendance(cursor, conn, student_id):
    """Mark attendance for a student. Returns True if successful."""
    try:
        today = datetime.now().date()
        
        # Check if already marked
        if is_already_marked(cursor, student_id, today):
            return False, "already_marked"
        
        # Insert attendance record
        current_time = datetime.now().time()
        cursor.execute(
            "INSERT INTO attendance (student_id, date, time, status) VALUES (%s, %s, %s, %s)",
            (student_id, today, current_time, "Present")
        )
        conn.commit()
        return True, current_time.strftime("%H:%M:%S")
    
    except Exception as e:
        print(f"Error marking attendance: {e}")
        return False, "error"


def start_attendance():
    """Main attendance loop - optimized for high FPS"""
    
    # Load encodings
    known_encodings, student_ids, student_names = load_encodings()
    if known_encodings is None:
        return
    
    # Connect to database
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # Load face detector
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    
    # Open camera with Windows optimization
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    print("\n" + "="*50)
    print("ATTENDANCE STARTED")
    print("="*50)
    print("Press 'Q' to quit\n")
    
    frame_count = 0
    recognized_count = 0
    marked_today = set()
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Only process every FRAME_SKIP frames to improve FPS
            if frame_count % FRAME_SKIP != 0:
                cv2.imshow("Smart Attendance", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                continue
            
            # Resize frame for faster processing (0.25 scale)
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.2, 5)
            
            # Process detected faces
            for (x, y, w, h) in faces:
                # Scale back to original frame size
                x, y, w, h = x*4, y*4, w*4, h*4
                
                # Extract face region
                face_region = frame[y:y+h, x:x+w]
                
                # Convert to RGB for face_recognition
                rgb_face = cv2.cvtColor(face_region, cv2.COLOR_BGR2RGB)
                
                # Get encoding for detected face
                try:
                    face_encodings = face_recognition.face_encodings(rgb_face)
                    
                    if face_encodings:
                        face_encoding = face_encodings[0]
                        
                        # Compare with known encodings
                        matches = face_recognition.compare_faces(
                            known_encodings,
                            face_encoding,
                            tolerance=TOLERANCE
                        )
                        distances = face_recognition.face_distance(known_encodings, face_encoding)
                        
                        if len(distances) > 0:
                            best_idx = np.argmin(distances)
                            best_dist = distances[best_idx]
                            
                            # If match found
                            if matches[best_idx]:
                                student_id = student_ids[best_idx]
                                student_name = student_names[best_idx]
                                
                                # Try to mark attendance
                                success, result = mark_attendance(cursor, conn, student_id)
                                
                                if success:
                                    marked_today.add(student_name)
                                    color = GREEN
                                    status = "✓ MARKED"
                                    recognized_count += 1
                                    print(f"✓ {student_name} marked at {result}")
                                
                                elif result == "already_marked":
                                    color = YELLOW
                                    status = "⚠ DUPLICATE"
                                else:
                                    color = RED
                                    status = "✗ ERROR"
                                
                                # Draw bounding box
                                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                                cv2.putText(frame, student_name, (x, y-30),
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                                cv2.putText(frame, status, (x, y-5),
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                except Exception as e:
                    pass  # Skip encoding errors silently
            
            # Display info on frame
            cv2.putText(frame, f"Marked: {len(marked_today)} | Recognized: {recognized_count}",
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, WHITE, 2)
            cv2.putText(frame, "Press Q to quit", (10, 470),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, WHITE, 1)
            
            cv2.imshow("Smart Attendance", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    finally:
        print("\n" + "="*50)
        print(f"Session ended. Students marked: {len(marked_today)}")
        print("="*50)
        cap.release()
        cv2.destroyAllWindows()
        cursor.close()
        conn.close()


if __name__ == "__main__":
    start_attendance()
