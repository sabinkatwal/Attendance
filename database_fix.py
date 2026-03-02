import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="sabindon",
    database="smart_attendance"
)
cursor = conn.cursor()

# Drop and recreate tables cleanly
cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
cursor.execute("DROP TABLE IF EXISTS attendance")
cursor.execute("DROP TABLE IF EXISTS students")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

cursor.execute("""
    CREATE TABLE students (
        student_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        department VARCHAR(100),
        roll_number VARCHAR(50) UNIQUE,
        enrolled_date DATE DEFAULT (CURDATE())
    )
""")

cursor.execute("""
    CREATE TABLE attendance (
        id INT AUTO_INCREMENT PRIMARY KEY,
        student_id INT,
        date DATE NOT NULL,
        time TIME NOT NULL,
        status VARCHAR(20) DEFAULT 'Present',
        FOREIGN KEY (student_id) REFERENCES students(student_id),
        UNIQUE KEY no_duplicate (student_id, date)
    )
""")

conn.commit()
conn.close()
print("✅ Tables fixed successfully! Now run register_student.py")