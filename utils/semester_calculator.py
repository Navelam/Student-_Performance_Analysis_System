# utils/semester_calculator.py

from datetime import datetime

def calculate_current_semester(admission_year):
    """
    Calculate current semester based on admission year and current date
    
    Rules:
    - June to November → Odd semester (1,3,5,7)
    - December to April → Even semester (2,4,6,8)
    - Max semester is 8
    
    Example:
        Admission: 2022
        Current: 2026
        year_diff = 4
        base_sem = 8
        If month >=6 → sem 9 → capped at 8
    
    Returns:
        int: Current semester (1-8)
    """
    today = datetime.now()
    current_year = today.year
    current_month = today.month
    
    # Calculate years since admission
    year_diff = current_year - admission_year
    
    # Base semesters (2 per year)
    base_sem = year_diff * 2
    
    # Determine if current month is in odd/even semester
    # June to November (6-11) → Odd semester
    # December to April (12-4) → Even semester
    if 6 <= current_month <= 11:  # Odd semester
        current_sem = base_sem + 1
    else:  # Even semester (Dec-Apr)
        current_sem = base_sem
    
    # Cap at 8 (max semesters)
    if current_sem > 8:
        current_sem = 8
    elif current_sem < 1:
        current_sem = 1
    
    return current_sem


def get_semester_type(current_month):
    """Return 'ODD' or 'EVEN' based on month"""
    return 'ODD' if 6 <= current_month <= 11 else 'EVEN'


def get_academic_year_from_semester(admission_year, semester):
    """
    Get academic year string for a given semester
    
    Example: 
        admission_year=2022, semester=3 → "2023-2024"
    """
    years_passed = (semester - 1) // 2
    start_year = admission_year + years_passed
    end_year = start_year + 1
    return f"{start_year}-{end_year}"


def get_semester_dates(admission_year, semester):
    """
    Get start and end dates for a given semester
    """
    from datetime import date
    
    years_passed = (semester - 1) // 2
    sem_year = admission_year + years_passed
    
    if semester % 2 == 1:  # Odd semester
        start_date = date(sem_year, 6, 1)
        end_date = date(sem_year, 11, 30)
    else:  # Even semester
        start_date = date(sem_year + 1, 12, 1)
        end_date = date(sem_year + 1, 4, 30)
    
    return start_date, end_date


def validate_semester_for_entry(student, target_semester):
    """
    Validate if a teacher can enter marks for a semester
    
    Teachers can ONLY enter marks for current semester
    """
    current_sem = student.current_semester
    return target_semester == current_sem


def get_batch_students(admission_year, department_id=None):
    """
    Get all students from a specific batch
    """
    from model import Student
    
    query = Student.query.filter_by(admission_year=admission_year)
    
    if department_id:
        query = query.filter_by(department_id=department_id)
    
    return query.all()