"""
Database Setup module - Initializes the database and creates tables.
"""

import mysql.connector
from mysql.connector import Error
import config
from logging_setup import get_logger

logger = get_logger(__name__)

def setup_database() -> None:
    """Initialize the database and create required tables."""
    try:
        # Connect without specifying database first
        db_config = config.DB_CONFIG.copy()
        db_name = db_config.pop("database")
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cursor.execute(f"USE {db_name}")
        logger.info(f"Database '{db_name}' ready")
        print(f"✅ Database '{db_name}' ready.")

        # Students table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                department VARCHAR(100),
                roll_number VARCHAR(50) UNIQUE,
                enrolled_date DATE DEFAULT (CURDATE())
            )
        """)
        logger.info("Students table ready")
        print("✅ Table 'students' ready.")

        # Attendance table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT,
                date DATE NOT NULL,
                time TIME NOT NULL,
                status VARCHAR(20) DEFAULT 'Present',
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                UNIQUE KEY no_duplicate (student_id, date)
            )
        """)
        logger.info("Attendance table ready")
        print("✅ Table 'attendance' ready.")

        conn.commit()
        conn.close()
        logger.info("Database setup complete")
        print("\n🎉 Database setup complete! You can now register students.")

    except Error as e:
        logger.error(f"Database setup error: {e}")
        print(f"❌ Error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during database setup: {e}")
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    setup_database()
