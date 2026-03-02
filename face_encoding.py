"""
Face Encoding module - Generates face encodings incrementally (only new students).
"""

import face_recognition
import os
import pickle
import cv2

DATASET_DIR = "dataset"
ENCODINGS_FILE = "encodings.pkl"

# Face recognition settings
JITTERS = 1  # Number of times to resample (1=fast, 2=more accurate)
MODEL = "hog"  # "hog" (fast) or "cnn" (accurate, requires GPU)


def get_existing_students():
    """Load student IDs and names from existing encodings.pkl"""
    if not os.path.exists(ENCODINGS_FILE):
        return set(), set()
    
    try:
        with open(ENCODINGS_FILE, "rb") as f:
            data = pickle.load(f)
            if isinstance(data, tuple) and len(data) == 3:
                _, student_ids, student_names = data
                existing_ids = set(sid for sid in student_ids if sid is not None)
                existing_names = set(student_names)
                return existing_ids, existing_names
    except Exception as e:
        print(f"Error loading existing encodings: {e}")
    
    return set(), set()


def extract_student_id(folder_name):
    """Extract student ID from folder name like '17_Sabin_Katwal'"""
    try:
        parts = folder_name.split("_", 1)
        if parts[0].isdigit():
            return int(parts[0])
    except:
        pass
    return None


def extract_student_name(folder_name):
    """Extract name from folder name like '17_Sabin_Katwal' → 'Sabin Katwal'"""
    parts = folder_name.split("_", 1)
    if len(parts) > 1:
        return parts[1].replace("_", " ")
    return folder_name


def encode_student(folder_path, student_id, student_name):
    """Encode all face images for a single student"""
    image_files = [
        f for f in os.listdir(folder_path)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]
    
    if not image_files:
        print(f"  ⚠ {student_name}: No images found")
        return None, 0, 0
    
    encodings = []
    success_count = 0
    fail_count = 0
    
    for img_file in image_files:
        img_path = os.path.join(folder_path, img_file)
        
        try:
            image = face_recognition.load_image_file(img_path)
            face_encodings = face_recognition.face_encodings(
                image,
                num_jitters=JITTERS,
                model=MODEL
            )
            
            if face_encodings:
                encodings.append(face_encodings[0])
                success_count += 1
            else:
                fail_count += 1
        
        except Exception as e:
            fail_count += 1
            print(f"    Error: {img_file} - {str(e)[:40]}")
    
    if encodings:
        return encodings, success_count, fail_count
    else:
        return None, success_count, fail_count


def generate_encodings():
    """
    Generate encodings INCREMENTALLY:
    - Load existing encodings.pkl
    - Only encode NEW students (not in existing file)
    - Append new encodings to existing file
    - Never overwrite previous encodings
    """
    
    if not os.path.exists(DATASET_DIR):
        print(f"❌ Folder '{DATASET_DIR}' not found.")
        print("   Run register_student.py first.")
        return
    
    # Get list of student folders
    student_folders = [
        f for f in os.listdir(DATASET_DIR)
        if os.path.isdir(os.path.join(DATASET_DIR, f))
    ]
    
    if not student_folders:
        print(f"❌ No student folders in {DATASET_DIR}/")
        return
    
    # Load existing encodings
    existing_ids, existing_names = get_existing_students()
    
    # Load current encodings data
    if os.path.exists(ENCODINGS_FILE):
        try:
            with open(ENCODINGS_FILE, "rb") as f:
                data = pickle.load(f)
                known_encodings, student_ids, student_names = data
            print(f"Loaded {len(set(student_ids))} existing students from {ENCODINGS_FILE}\n")
        except Exception as e:
            print(f"Error loading encodings: {e}")
            known_encodings, student_ids, student_names = [], [], []
    else:
        known_encodings, student_ids, student_names = [], [], []
        print(f"Creating new {ENCODINGS_FILE}\n")
    
    # Find NEW students to encode
    new_students = []
    for folder in student_folders:
        sid = extract_student_id(folder)
        sname = extract_student_name(folder)
        
        # Check if this student already exists
        if sid and sid in existing_ids:
            continue
        if sname in existing_names:
            continue
        
        new_students.append((folder, sid, sname))
    
    if not new_students:
        print("✅ All students already encoded. Nothing to do.")
        return
    
    # Encode new students
    print(f"Encoding {len(new_students)} NEW student(s)...\n")
    
    total_new_encodings = 0
    total_images = 0
    total_failed = 0
    
    for folder, sid, sname in new_students:
        folder_path = os.path.join(DATASET_DIR, folder)
        
        encodings, success, fail = encode_student(folder_path, sid, sname)
        image_count = success + fail
        total_images += image_count
        total_failed += fail
        
        if encodings:
            # Add to lists
            for enc in encodings:
                known_encodings.append(enc)
                student_ids.append(sid)
                student_names.append(sname)
            
            total_new_encodings += len(encodings)
            print(f"  ✓ {sname}: {success}/{image_count} images encoded")
        else:
            print(f"  ✗ {sname}: Failed to encode")
    
    # Save updated encodings
    try:
        with open(ENCODINGS_FILE, "wb") as f:
            pickle.dump((known_encodings, student_ids, student_names), f)
        
        unique_students = len(set(student_ids))
        
        print("\n" + "="*50)
        print("Encoding Complete!")
        print(f"  Total students   : {unique_students}")
        print(f"  Total encodings  : {len(known_encodings)}")
        print(f"  New encodings    : {total_new_encodings}")
        print(f"  Failed images    : {total_failed}")
        print(f"  Saved to         : {ENCODINGS_FILE}")
        print("="*50)
        print("\nReady! Run attendance.py to start marking attendance.")
    
    except Exception as e:
        print(f"❌ Failed to save encodings: {e}")


if __name__ == "__main__":
    generate_encodings()