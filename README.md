# Smart Attendance System - Refactored & Optimized

A minimal, clean, and high-performance face recognition attendance system built with Python, OpenCV, and MySQL.

## ✅ System Features

- **Incremental Face Encoding**: Only new students are encoded; existing encodings are never overwritten
- **Exactly 20 Face Images**: Registration captures precisely 20 images per student
- **High FPS Performance**: Optimized for ~50 FPS real-time recognition on Windows
- **Windows Optimized**: Uses `cv2.CAP_DSHOW` for faster camera access
- **No Logging Framework**: Simple, beginner-friendly code
- **Clean Architecture**: Only 3 Python files needed

---

## 📁 Project File Structure
```
attendance_system/
│
├── main_gui.py             ← 🖥  Main dashboard (run this)
├── auto_attendance.py      ← 📷  Face recognition + attendance marking
├── register_student.py     ← 👤  Register new student + capture faces
├── face_encoding.py        ← 🧠  Generate face encodings (encodings.pkl)
├── view_attendance.py      ← 📋  View and export reports
├── database_setup.py       ← 🗄  Create MySQL database and tables
│
├── dataset/                ← Auto-created: student face images
├── trainer/                ← Auto-created: model files
├── attendance/             ← Auto-created: exported CSV reports
├── haarcascade/
│   └── haarcascade_frontalface_default.xml   ← Required!
│
├── encodings.pkl           ← Auto-created after running face_encoding.py
└── README.md
```

---

## ▶ How to Run (Step by Step)

### Step 1: Setup Database (only once)
```bash
python database_setup.py
```

### Step 2: Register a Student
```bash
python register_student.py
```
- Enter name, department, roll number
- 60 face images will be captured from your webcam

### Step 3: Generate Face Encodings (after each new student)
```bash
python face_encoding.py
```

### Step 4: Start Attendance
```bash
python auto_attendance.py
```
- Press `Q` to stop

### OR: Launch the Full Dashboard
```bash
python main_gui.py
```
All features available from one window.

---

## 🗄 Database Password
Default password in all files: `sabindon`
To change it, find and replace `"sabindon"` in all .py files.

---

## 📦 Required Libraries
```
opencv-python
opencv-contrib-python
face_recognition
numpy
Pillow
pandas
mysql-connector-python
```
Install all: `pip install opencv-python opencv-contrib-python face_recognition numpy Pillow pandas mysql-connector-python`

---

## ⚠️ Common Issues

| Problem | Fix |
|---|---|
| `encodings.pkl not found` | Run `face_encoding.py` first |
| `Database connection error` | Check MySQL is running + password is correct |
| `dlib install fails` | Install cmake first: `pip install cmake` then retry |
| Camera not opening | Check webcam is connected and not used by another app |
| Low recognition accuracy | Register more images (increase to 100), ensure good lighting |
