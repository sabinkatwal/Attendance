"""
Attendance Viewer module - View and export attendance records.
"""

import mysql.connector
from mysql.connector import Error
import pandas as pd
import os
from datetime import date, datetime
from typing import List, Optional, Tuple
import config
from logging_setup import get_logger

logger = get_logger(__name__)

def get_connection():
    """Get a database connection."""
    try:
        return mysql.connector.connect(**config.DB_CONFIG)
    except Error as e:
        logger.error(f"Database connection error: {e}")
        raise

def view_today() -> None:
    """Print today's attendance to console."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        today = date.today()

        cursor.execute("""
            SELECT s.roll_number, s.name, s.department, a.time, a.status
            FROM attendance a
            JOIN students s ON a.student_id = s.student_id
            WHERE a.date = %s
            ORDER BY a.time
        """, (today,))

        rows = cursor.fetchall()
        conn.close()

        print(f"\n📋 Attendance for {today.strftime('%B %d, %Y')}")
        print("-" * 65)
        print(f"{'Roll No':<12} {'Name':<25} {'Department':<15} {'Time':<10} Status")
        print("-" * 65)

        if not rows:
            print("  No attendance recorded today.")
        else:
            for row in rows:
                print(f"{row[0]:<12} {row[1]:<25} {row[2]:<15} {str(row[3])[:8]:<10} {row[4]}")

        print(f"-" * 65)
        print(f"  Total present: {len(rows)}")
        logger.info(f"Viewed today's attendance ({len(rows)} present)")

    except Error as e:
        logger.error(f"Database error viewing today's attendance: {e}")
        print(f"❌ Database error: {e}")

def view_by_date(target_date: str) -> None:
    """
    View attendance for a specific date.
    
    Args:
        target_date: Date in format YYYY-MM-DD
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT s.roll_number, s.name, s.department, a.time, a.status
            FROM attendance a
            JOIN students s ON a.student_id = s.student_id
            WHERE a.date = %s
            ORDER BY a.time
        """, (target_date,))

        rows = cursor.fetchall()
        conn.close()

        print(f"\n📋 Attendance for {target_date}")
        print("-" * 65)
        print(f"{'Roll No':<12} {'Name':<25} {'Department':<15} {'Time':<10} Status")
        print("-" * 65)
        if not rows:
            print("  No records found for this date.")
        else:
            for row in rows:
                print(f"{row[0]:<12} {row[1]:<25} {row[2]:<15} {str(row[3])[:8]:<10} {row[4]}")
        print(f"  Total: {len(rows)}")
        logger.info(f"Viewed attendance for {target_date} ({len(rows)} records)")

    except Error as e:
        logger.error(f"Database error viewing attendance for {target_date}: {e}")
        print(f"❌ Database error: {e}")

def view_student(name_or_roll: str) -> None:
    """
    View all attendance records for a specific student.
    
    Args:
        name_or_roll: Student name or roll number
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT a.date, a.time, a.status
            FROM attendance a
            JOIN students s ON a.student_id = s.student_id
            WHERE s.name LIKE %s OR s.roll_number = %s
            ORDER BY a.date DESC
        """, (f"%{name_or_roll}%", name_or_roll))

        rows = cursor.fetchall()
        conn.close()

        print(f"\n📋 Attendance records for '{name_or_roll}'")
        print("-" * 40)
        if not rows:
            print("  No records found.")
        else:
            for row in rows:
                print(f"  {row[0]}  {str(row[1])[:8]}  {row[2]}")
        print(f"  Total days present: {len(rows)}")
        logger.info(f"Viewed student attendance for {name_or_roll} ({len(rows)} days)")

    except Error as e:
        logger.error(f"Database error viewing student attendance: {e}")
        print(f"❌ Database error: {e}")

def list_students() -> None:
    """List all registered students."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT student_id, roll_number, name, department, enrolled_date FROM students ORDER BY student_id")
        rows = cursor.fetchall()
        conn.close()

        print(f"\n👥 Registered Students ({len(rows)} total)")
        print("-" * 70)
        print(f"{'ID':<6} {'Roll No':<12} {'Name':<25} {'Department':<15} Enrolled")
        print("-" * 70)
        for row in rows:
            print(f"{row[0]:<6} {row[1]:<12} {row[2]:<25} {row[3]:<15} {row[4]}")
        logger.info(f"Listed {len(rows)} students")

    except Error as e:
        logger.error(f"Database error listing students: {e}")
        print(f"❌ Database error: {e}")

def export_to_csv(start_date: Optional[str] = None, end_date: Optional[str] = None) -> Optional[str]:
    """
    Export attendance records to CSV.
    
    Args:
        start_date: Optional start date (YYYY-MM-DD)
        end_date: Optional end date (YYYY-MM-DD)
        
    Returns:
        Path to exported CSV file, or None on error
    """
    try:
        conn = get_connection()

        query = """
            SELECT s.roll_number AS 'Roll Number', s.name AS 'Name',
                   s.department AS 'Department', a.date AS 'Date',
                   a.time AS 'Time', a.status AS 'Status'
            FROM attendance a
            JOIN students s ON a.student_id = s.student_id
        """
        params = []

        if start_date and end_date:
            query += " WHERE a.date BETWEEN %s AND %s"
            params = [start_date, end_date]
        elif start_date:
            query += " WHERE a.date = %s"
            params = [start_date]

        query += " ORDER BY a.date DESC, s.name"

        df = pd.read_sql(query, conn, params=params)
        conn.close()

        os.makedirs(config.ATTENDANCE_EXPORT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{config.ATTENDANCE_EXPORT_DIR}/report_{timestamp}.csv"
        df.to_csv(filename, index=False)
        logger.info(f"Exported {len(df)} attendance records to {filename}")
        print(f"✅ Report exported: {filename} ({len(df)} records)")
        return filename

    except Error as e:
        logger.error(f"Database error during export: {e}")
        print(f"❌ Database error: {e}")
        return None
    except Exception as e:
        logger.error(f"Error during export: {e}")
        print(f"❌ Error during export: {e}")
        return None

if __name__ == "__main__":
    print("=" * 40)
    print("   ATTENDANCE REPORT VIEWER")
    print("=" * 40)
    print("1. Today's attendance")
    print("2. By specific date")
    print("3. By student")
    print("4. List all students")
    print("5. Export all to CSV")
    print("=" * 40)
    choice = input("Choose option (1-5): ").strip()

    if choice == "1":
        view_today()
    elif choice == "2":
        d = input("Enter date (YYYY-MM-DD): ").strip()
        view_by_date(d)
    elif choice == "3":
        s = input("Enter student name or roll number: ").strip()
        view_student(s)
    elif choice == "4":
        list_students()
    elif choice == "5":
        export_to_csv()
    else:
        print("Invalid option.")
