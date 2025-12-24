"""
ZAD Education Platform - Bulk Import Service | منصة زاد - خدمة الاستيراد الجماعي
================================================================================
CSV/Excel import for users and grades.
"""

import io
from typing import List, Tuple, Optional
from werkzeug.security import generate_password_hash
from core.database import get_db_session
from models import User, School, Grade


def parse_csv_users(file_content: bytes, school_id: int) -> Tuple[List[dict], List[str]]:
    """
    Parse CSV file content for user import.
    
    Expected CSV columns: email, full_name, role, password (optional)
    
    Args:
        file_content: CSV file bytes
        school_id: Target school ID
        
    Returns:
        Tuple of (valid_users, errors)
    """
    import csv
    
    valid_users = []
    errors = []
    
    try:
        # Decode and parse CSV
        content = file_content.decode('utf-8-sig')  # Handle BOM
        reader = csv.DictReader(io.StringIO(content))
        
        required_columns = ['email', 'full_name', 'role']
        
        # Check columns
        if not all(col in (reader.fieldnames or []) for col in required_columns):
            missing = [col for col in required_columns if col not in (reader.fieldnames or [])]
            errors.append(f"Missing required columns: {missing}")
            return [], errors
        
        for row_num, row in enumerate(reader, start=2):  # Start at 2 (1 is header)
            email = row.get('email', '').strip()
            full_name = row.get('full_name', '').strip()
            role = row.get('role', '').strip().lower()
            password = row.get('password', '').strip() or 'ZAD@123'  # Default password
            
            # Validate
            if not email:
                errors.append(f"Row {row_num}: Email is required")
                continue
            
            if not full_name:
                errors.append(f"Row {row_num}: Full name is required")
                continue
            
            valid_roles = ['student', 'teacher', 'school_admin']
            if role not in valid_roles:
                errors.append(f"Row {row_num}: Invalid role '{role}'. Must be one of {valid_roles}")
                continue
            
            valid_users.append({
                'email': email,
                'full_name': full_name,
                'role': role,
                'password': password,
                'school_id': school_id
            })
        
    except Exception as e:
        errors.append(f"CSV parsing error: {str(e)}")
    
    return valid_users, errors


def parse_excel_users(file_content: bytes, school_id: int) -> Tuple[List[dict], List[str]]:
    """
    Parse Excel file content for user import.
    
    Args:
        file_content: Excel file bytes
        school_id: Target school ID
        
    Returns:
        Tuple of (valid_users, errors)
    """
    errors = []
    valid_users = []
    
    try:
        import pandas as pd
        
        df = pd.read_excel(io.BytesIO(file_content))
        
        required_columns = ['email', 'full_name', 'role']
        missing = [col for col in required_columns if col not in df.columns]
        
        if missing:
            errors.append(f"Missing required columns: {missing}")
            return [], errors
        
        for idx, row in df.iterrows():
            row_num = idx + 2  # Account for header
            
            email = str(row.get('email', '')).strip()
            full_name = str(row.get('full_name', '')).strip()
            role = str(row.get('role', '')).strip().lower()
            password = str(row.get('password', '')).strip() or 'ZAD@123'
            
            if not email or email == 'nan':
                errors.append(f"Row {row_num}: Email is required")
                continue
            
            if not full_name or full_name == 'nan':
                errors.append(f"Row {row_num}: Full name is required")
                continue
            
            valid_roles = ['student', 'teacher', 'school_admin']
            if role not in valid_roles:
                errors.append(f"Row {row_num}: Invalid role '{role}'")
                continue
            
            valid_users.append({
                'email': email,
                'full_name': full_name,
                'role': role,
                'password': password,
                'school_id': school_id
            })
            
    except ImportError:
        errors.append("pandas library not installed. Run: pip install pandas openpyxl")
    except Exception as e:
        errors.append(f"Excel parsing error: {str(e)}")
    
    return valid_users, errors


def import_users(users: List[dict]) -> Tuple[int, int, List[str]]:
    """
    Import users to database.
    
    Args:
        users: List of user dicts with email, full_name, role, password, school_id
        
    Returns:
        Tuple of (success_count, skip_count, errors)
    """
    session = get_db_session()
    success = 0
    skipped = 0
    errors = []
    
    try:
        for user_data in users:
            # Check if email already exists
            existing = session.query(User).filter(
                User.email == user_data['email']
            ).first()
            
            if existing:
                skipped += 1
                errors.append(f"Skipped {user_data['email']}: Email already exists")
                continue
            
            new_user = User(
                email=user_data['email'],
                full_name=user_data['full_name'],
                role=user_data['role'],
                hashed_password=generate_password_hash(user_data['password']),
                school_id=user_data['school_id'],
                is_active=True
            )
            
            session.add(new_user)
            success += 1
        
        session.commit()
        
    except Exception as e:
        session.rollback()
        errors.append(f"Database error: {str(e)}")
    
    finally:
        session.close()
    
    return success, skipped, errors


def parse_csv_grades(file_content: bytes, school_id: int) -> Tuple[List[dict], List[str]]:
    """
    Parse CSV file for grade import.
    
    Expected columns: student_email, subject, score, max_score, feedback (optional)
    
    Args:
        file_content: CSV file bytes
        school_id: Target school ID
        
    Returns:
        Tuple of (valid_grades, errors)
    """
    import csv
    
    valid_grades = []
    errors = []
    
    try:
        content = file_content.decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(content))
        
        required_columns = ['student_email', 'subject', 'score', 'max_score']
        
        if not all(col in (reader.fieldnames or []) for col in required_columns):
            missing = [col for col in required_columns if col not in (reader.fieldnames or [])]
            errors.append(f"Missing required columns: {missing}")
            return [], errors
        
        session = get_db_session()
        
        try:
            for row_num, row in enumerate(reader, start=2):
                student_email = row.get('student_email', '').strip()
                subject = row.get('subject', '').strip()
                
                try:
                    score = float(row.get('score', 0))
                    max_score = int(row.get('max_score', 100))
                except ValueError:
                    errors.append(f"Row {row_num}: Invalid score or max_score")
                    continue
                
                feedback = row.get('feedback', '').strip()
                
                # Look up student
                student = session.query(User).filter(
                    User.email == student_email,
                    User.school_id == school_id,
                    User.role == 'student'
                ).first()
                
                if not student:
                    errors.append(f"Row {row_num}: Student '{student_email}' not found")
                    continue
                
                valid_grades.append({
                    'student_id': student.id,
                    'school_id': school_id,
                    'subject': subject,
                    'score': score,
                    'max_score': max_score,
                    'feedback': feedback
                })
        finally:
            session.close()
            
    except Exception as e:
        errors.append(f"CSV parsing error: {str(e)}")
    
    return valid_grades, errors


def import_grades(grades: List[dict]) -> Tuple[int, List[str]]:
    """
    Import grades to database.
    
    Args:
        grades: List of grade dicts
        
    Returns:
        Tuple of (success_count, errors)
    """
    session = get_db_session()
    success = 0
    errors = []
    
    try:
        for grade_data in grades:
            new_grade = Grade(
                student_id=grade_data['student_id'],
                school_id=grade_data['school_id'],
                subject=grade_data['subject'],
                score=grade_data['score'],
                max_score=grade_data['max_score'],
                feedback=grade_data['feedback']
            )
            
            session.add(new_grade)
            success += 1
        
        session.commit()
        
    except Exception as e:
        session.rollback()
        errors.append(f"Database error: {str(e)}")
    
    finally:
        session.close()
    
    return success, errors


def generate_user_template() -> str:
    """Generate CSV template for user import."""
    return """email,full_name,role,password
student1@school.edu,Ahmed Mohammed,student,
student2@school.edu,Fatima Ali,student,
teacher1@school.edu,Dr. Hassan Ibrahim,teacher,
"""


def generate_grades_template() -> str:
    """Generate CSV template for grade import."""
    return """student_email,subject,score,max_score,feedback
student1@school.edu,Mathematics,85,100,Great work!
student2@school.edu,Science,92,100,Excellent understanding
"""
