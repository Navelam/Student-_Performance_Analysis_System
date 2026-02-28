# utils/scheduler.py
"""
Exam Timetable Scheduler Utility
Handles auto-splitting and date distribution for all departments
"""

import random
import math
from datetime import datetime, timedelta
from typing import List, Tuple, Any

def split_subjects_equally(subjects: List[Any]) -> Tuple[List[Any], List[Any]]:
    """
    Split subjects equally between 10AM and 2PM sessions.
    Works for any list of subjects regardless of department.
    """
    if not subjects:
        return [], []
    
    subjects_copy = subjects.copy()
    random.shuffle(subjects_copy)
    split_point = math.ceil(len(subjects_copy) / 2)
    
    return subjects_copy[:split_point], subjects_copy[split_point:]

def distribute_across_dates(subjects: List[Any], start_date, end_date, time_slot: str) -> List[dict]:
    """
    Distribute subjects equally across a date range.
    Ensures even distribution regardless of department.
    """
    if not subjects:
        return []
    
    total_days = (end_date - start_date).days + 1
    if total_days <= 0:
        return []
    
    dates = [start_date + timedelta(days=i) for i in range(total_days)]
    shuffled = subjects.copy()
    random.shuffle(shuffled)
    
    subjects_per_day = math.ceil(len(subjects) / total_days)
    schedule = []
    idx = 0
    
    for date in dates:
        day_subjects = shuffled[idx:idx + subjects_per_day]
        for subject in day_subjects:
            schedule.append({
                'subject': subject,
                'date': date,
                'time': time_slot,
                'department': subject.department.name,
                'semester': subject.semester_id
            })
        idx += subjects_per_day
        if idx >= len(shuffled):
            break
    
    return schedule

def get_semesters_by_cycle(cycle: str) -> List[int]:
    """
    Get semester list based on exam cycle.
    
    Args:
        cycle: 'ODD' (1,3,5,7), 'EVEN' (2,4,6,8), or 'FULL' (1-8)
    
    Returns:
        List of semester numbers
    """
    if cycle == 'ODD':
        return [1, 3, 5, 7]
    elif cycle == 'EVEN':
        return [2, 4, 6, 8]
    else:  # FULL
        return [1, 2, 3, 4, 5, 6, 7, 8]

def validate_no_duplicates(subjects_10am: List[Any], subjects_2pm: List[Any]) -> bool:
    """Validate that no subject appears in both sessions"""
    ids_10am = {s.id for s in subjects_10am}
    ids_2pm = {s.id for s in subjects_2pm}
    return len(ids_10am.intersection(ids_2pm)) == 0

def get_split_statistics(subjects_10am: List[Any], subjects_2pm: List[Any]) -> dict:
    """Get statistics about the split"""
    total = len(subjects_10am) + len(subjects_2pm)
    
    return {
        'total': total,
        'morning': len(subjects_10am),
        'afternoon': len(subjects_2pm),
        'morning_pct': round((len(subjects_10am) / total) * 100, 1) if total > 0 else 0,
        'afternoon_pct': round((len(subjects_2pm) / total) * 100, 1) if total > 0 else 0,
        'valid': validate_no_duplicates(subjects_10am, subjects_2pm)
    }

def group_subjects_by_department(subjects: List[Any]) -> dict:
    """Group subjects by department name"""
    result = {}
    for subject in subjects:
        dept_name = subject.department.name
        if dept_name not in result:
            result[dept_name] = []
        result[dept_name].append(subject)
    return result

def get_academic_years_range(start_year=None, end_year=None):
    """Generate a list of academic years within a range"""
    if start_year is None:
        start_year = datetime.now().year - 2
    if end_year is None:
        end_year = datetime.now().year + 5
    
    years = []
    for year in range(start_year, end_year):
        years.append(f"{year}-{year+1}")
    return years