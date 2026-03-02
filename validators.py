"""
Input validation utilities for Smart Attendance System.
Validates user inputs before database operations.
"""

import re
from typing import Tuple, Optional


def validate_name(name: str) -> Tuple[bool, str]:
    """
    Validate student name.
    
    Args:
        name: Student name to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name or not isinstance(name, str):
        return False, "Name is required and must be text"
    
    name = name.strip()
    if len(name) < 2:
        return False, "Name must be at least 2 characters"
    
    if len(name) > 100:
        return False, "Name must not exceed 100 characters"
    
    if not re.match(r"^[a-zA-Z\s\.\-\']+$", name):
        return False, "Name contains invalid characters (only letters, spaces, dots, hyphens, apostrophes allowed)"
    
    return True, ""


def validate_roll_number(roll: str) -> Tuple[bool, str]:
    """
    Validate roll number format.
    
    Args:
        roll: Roll number to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not roll or not isinstance(roll, str):
        return False, "Roll number is required and must be text"
    
    roll = roll.strip()
    if len(roll) < 2:
        return False, "Roll number must be at least 2 characters"
    
    if len(roll) > 50:
        return False, "Roll number must not exceed 50 characters"
    
    if not re.match(r"^[a-zA-Z0-9\-\.]+$", roll):
        return False, "Roll number contains invalid characters (only alphanumeric, hyphens, dots allowed)"
    
    return True, ""


def validate_department(dept: str) -> Tuple[bool, str]:
    """
    Validate department name.
    
    Args:
        dept: Department name to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not dept or not isinstance(dept, str):
        return False, "Department is required and must be text"
    
    dept = dept.strip()
    if len(dept) < 2:
        return False, "Department must be at least 2 characters"
    
    if len(dept) > 100:
        return False, "Department must not exceed 100 characters"
    
    if not re.match(r"^[a-zA-Z\s\&\-\.]+$", dept):
        return False, "Department contains invalid characters"
    
    return True, ""


def validate_student_input(name: str, roll_number: str, department: str = "") -> Tuple[bool, str]:
    """
    Validate all student input fields together.
    
    Args:
        name: Student name
        roll_number: Student roll number
        department: Student department (optional)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate name
    valid, msg = validate_name(name)
    if not valid:
        return False, f"Name: {msg}"
    
    # Validate roll number
    valid, msg = validate_roll_number(roll_number)
    if not valid:
        return False, f"Roll Number: {msg}"
    
    # Validate department if provided
    if department.strip():
        valid, msg = validate_department(department)
        if not valid:
            return False, f"Department: {msg}"
    
    return True, ""
