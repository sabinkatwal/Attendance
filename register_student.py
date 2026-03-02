"""
Student Registration module - Registers new students and captures exactly 20 face images.
"""

import cv2
import os
import mysql.connector

# Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "1234",
    "database": "smart_attendance"
}

DATASET_DIR = "dataset"
IMAGES_PER_STUDENT = 20  # Exactly 20 images


def register_student():
    """Register a new student and capture 20 face images."""
    
    # ── Get student info ──────────────────────────────────────
    print("\n" + "="*50)
    print("STUDENT REGISTRATION")
    print("="*50)
    
    name = input("Enter student name: ").strip()
    roll_number = input("Enter roll number: ").strip()
    department = input("Enter department: ").strip()
    
    if not name or not roll_number or not department:
        print("❌ All fields are required.")
        return
    
    # ── Check if student already exists ───────────────────────
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("SELECT student_id FROM students WHERE roll_number = %s", (roll_number,))
        if cursor.fetchone():
            print(f"❌ Roll number '{roll_number}' already exists.")
            cursor.close()
            conn.close()
            return
        
        # ── Insert into database ──────────────────────────────
        cursor.execute(
            "INSERT INTO students (name, roll_number, department, date_registered) VALUES (%s, %s, %s, CURDATE())",
            (name, roll_number, department)
        )
        conn.commit()
        student_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        print(f"✅ Student registered with ID: {student_id}")
        
    except mysql.connector.Error as e:
        print(f"❌ Database error: {e}")
        return
    
    # ── Capture 20 face images ────────────────────────────────
    print(f"\n📷 Capturing {IMAGES_PER_STUDENT} face images...")
    print("Make sure your face is clearly visible in the frame.")
    print("Press SPACE to capture each image. Press ESC to cancel.\n")
    
    # Create dataset folder
    os.makedirs(DATASET_DIR, exist_ok=True)
    
    # Create student folder: ID_Name
    student_folder = os.path.join(DATASET_DIR, f"{student_id}_{name.replace(' ', '_')}")
    os.makedirs(student_folder, exist_ok=True)
    
    # Initialize camera
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Windows optimization
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    # Face detector
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    
    image_count = 0
    
    try:
        while image_count < IMAGES_PER_STUDENT:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to read from camera.")
                break
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            # Draw rectangles around faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Display progress
            cv2.putText(frame, f"Captured: {image_count}/{IMAGES_PER_STUDENT}",
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, "SPACE: Capture | ESC: Cancel",
                       (10, 470), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.imshow("Registration - Capture Face Images", frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == 32:  # SPACE
                if len(faces) > 0:
                    # Save image
                    img_path = os.path.join(student_folder, f"image_{image_count+1:03d}.jpg")
                    cv2.imwrite(img_path, frame)
                    image_count += 1
                    print(f"  ✓ Image {image_count} captured")
                else:
                    print("  ⚠ No face detected. Try again.")
            
            elif key == 27:  # ESC
                print("\n❌ Registration cancelled.")
                break
        
        # Check if we captured enough images
        if image_count == IMAGES_PER_STUDENT:
            print(f"\n✅ Successfully captured {IMAGES_PER_STUDENT} images for {name}!")
            print("Run face_encoding.py to generate encodings.")
        else:
            print(f"\n⚠ Only captured {image_count} images. Run registration again.")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    register_student()