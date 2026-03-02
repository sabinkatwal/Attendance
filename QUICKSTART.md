"""
QUICK START GUIDE - Smart Attendance System v2.0
=================================================
"""

# Step 1: Install Python dependencies
# ================================
pip install -r requirements.txt

# Step 2: Configure environment variables  
# =====================================
# Copy .env.example to .env
# Edit .env and add your MySQL credentials:
#   DB_PASSWORD=your_password_here

# Step 3: Setup Database (run once)
# ===============================
python database_setup.py
# This creates the smart_attendance database and tables

# Step 4: Option A - Use GUI (Recommended)
# =====================================
python main_gui.py
# Click "REGISTER STUDENT" to add new students
# Click "UPDATE FACE MODEL" after adding students
# Click "START ATTENDANCE" to mark attendance
# Click "EXPORT CSV REPORT" to export records

# Step 4: Option B - Use Command Line
# ==============================

# Register a student
python register_student.py
# Follow prompts, capture 40 face images

# Generate face encodings
python face_encoding.py
# Creates encodings.pkl from captured photos

# Start attendance
python auto_attendance.py
# Real-time face recognition and marking
# Press Q to quit

# View attendance
python view_attendance.py
# View today's attendance or specific dates

# Configuration Files
# ==================
.env                    # Environment variables (don't commit!)
.env.example           # Template (safe to commit)
config.py              # Configuration loader
requirements.txt       # Python dependencies

# Output Directories (auto-created)
# ================================
logs/                  # Application logs
dataset/               # Student face photos
attendance/            # Exported CSV reports

# Troubleshooting
# ==============

# If database connection fails:
# 1. Check MySQL is running
# 2. Verify credentials in .env
# 3. Run: python database_setup.py

# If face recognition is inaccurate:
# 1. Edit .env and increase FACE_RECOGNITION_JITTERS to 5
# 2. Register more photos per student
# 3. Improve lighting conditions
# 4. Ensure faces are clearly visible

# If encodings.pkl not found:
# 1. Run: python face_encoding.py
# 2. This creates the face model from registered photos

# Check Logs
# ==========
# All operations logged to: logs/smart_attendance.log
# Check this file for detailed error information

"""Tips:
1. Always run database_setup.py first
2. Register at least 3 students before testing
3. Use good lighting for best results
4. Keep faces clear in photos (not tilted)
5. Check logs/ directory if something fails
"""
