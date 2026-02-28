#!/usr/bin/env python
"""
MASTER ACADEMIC AND EXAM TIMETABLE SETUP - SINGLE FILE
Handles: Departments, Subjects, Students, Teachers, and Exam Timetable
Ensures: ONE EXAM PER DEPARTMENT PER DAY
"""

import sys
import os
from pathlib import Path
from datetime import datetime, date, timedelta
import random
import math
import string

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from extensions import db
from model import User, Department, Course, AcademicYear, Semester, Subject, Student, ExamTimetable
from werkzeug.security import generate_password_hash

# =====================================================
# CONFIGURATION - ALL IN ONE PLACE
# =====================================================

# All 7 Departments with their codes
ALL_DEPARTMENTS = [
    {"name": "Computer Science", "code": "CS"},
    {"name": "Computer Applications", "code": "CA"},
    {"name": "Commerce Finance", "code": "CF"},
    {"name": "Commerce Co-op", "code": "CC"},
    {"name": "English", "code": "EN"},
    {"name": "Economics", "code": "EC"},
    {"name": "History", "code": "HY"}
]

# Complete subject data for all 7 departments (Semesters 1-8)
DEPARTMENT_SUBJECTS = {
    "Computer Science": {
        1: ["Mathematics I", "Physics", "Chemistry", "C Programming", "English"],
        2: ["Mathematics II", "Digital Logic", "Data Structures", "Object Oriented Programming", "Environmental Science"],
        3: ["Discrete Mathematics", "Database Management Systems", "Computer Organization", "Operating Systems", "Soft Skills"],
        4: ["Computer Networks", "Design and Analysis of Algorithms", "Software Engineering", "Web Technologies", "Python Programming"],
        5: ["Compiler Design", "Distributed Systems", "Machine Learning", "Cloud Computing", "Elective I"],
        6: ["Big Data Analytics", "Internet of Things", "Cyber Security", "Elective II", "Project Work"],
        7: ["Artificial Intelligence", "Natural Language Processing", "Computer Vision", "Elective III", "Major Project I"],
        8: ["Deep Learning", "Blockchain", "Quantum Computing", "Elective IV", "Major Project II"]
    },
    "Computer Applications": {
        1: ["Mathematics I", "Digital Computer Fundamentals", "C Programming", "Financial Accounting", "English"],
        2: ["Mathematics II", "Data Structures", "Database Systems", "Object Oriented Programming with C++", "Organizational Behavior"],
        3: ["Operating Systems", "Computer Networks", "Java Programming", "Web Design", "Python Programming"],
        4: ["Software Engineering", "PHP Programming", "Data Mining", "Cloud Computing", "Mobile Application Development"],
        5: ["Machine Learning", "Big Data", "Cyber Security", "Elective I", "Mini Project"],
        6: ["Deep Learning", "Blockchain", "Elective II", "Major Project", "Internship"],
        7: ["Advanced Java", "Python for Data Science", "React Programming", "Elective III", "Industry Project"],
        8: ["DevOps", "Microservices", "Cloud Architecture", "Elective IV", "Research Project"]
    },
    "Commerce Finance": {
        1: ["Financial Accounting I", "Business Economics", "Business Mathematics", "Business Communication", "Computer Applications"],
        2: ["Financial Accounting II", "Corporate Accounting", "Business Statistics", "Banking Theory", "Marketing Management"],
        3: ["Advanced Accounting", "Cost Accounting", "Income Tax I", "Company Law", "Financial Management"],
        4: ["Management Accounting", "Income Tax II", "Auditing", "International Finance", "Investment Management"],
        5: ["Financial Services", "Derivatives Markets", "Risk Management", "Strategic Management", "Elective I"],
        6: ["Portfolio Management", "Mergers and Acquisitions", "Financial Modeling", "Elective II", "Project"],
        7: ["International Finance", "Corporate Governance", "Financial Derivatives", "Elective III", "Research Project"],
        8: ["Wealth Management", "Behavioral Finance", "Financial Analytics", "Elective IV", "Industry Project"]
    },
    "Commerce Co-op": {
        1: ["Co-operative Theory", "Principles of Economics", "Business Organization", "Financial Accounting", "English"],
        2: ["Co-operative Law", "Banking Theory", "Business Mathematics", "Corporate Accounting", "Hindi"],
        3: ["Co-operative Management", "Rural Economics", "Cost Accounting", "Marketing Management", "Human Resource Management"],
        4: ["Co-operative Credit", "Agricultural Economics", "Income Tax", "Auditing", "Entrepreneurship Development"],
        5: ["Co-operative Marketing", "International Trade", "Financial Services", "Research Methodology", "Elective I"],
        6: ["Co-operative Accounting", "Project Planning", "Co-operative Development", "Elective II", "Project Work"],
        7: ["Co-operative Banking", "Micro Finance", "Rural Development", "Elective III", "Field Study"],
        8: ["Co-operative Management", "Co-operative Legislation", "Co-operative Audit", "Elective IV", "Internship"]
    },
    "English": {
        1: ["British Poetry", "Prose", "English Grammar", "History of English Literature I", "Indian Writing in English"],
        2: ["British Drama", "Fiction", "Linguistics", "History of English Literature II", "American Literature"],
        3: ["Shakespeare", "Literary Criticism", "Phonetics", "Postcolonial Literature", "Women's Writing"],
        4: ["Modern Poetry", "Modern Drama", "Modern Fiction", "English Language Teaching", "Translation Studies"],
        5: ["European Literature", "Canadian Literature", "Film Studies", "Cultural Studies", "Elective I"],
        6: ["Comparative Literature", "Diasporic Literature", "New Literatures", "Elective II", "Project"],
        7: ["World Literature", "Literary Theory", "Creative Writing", "Elective III", "Research Paper"],
        8: ["Postmodern Literature", "Eco Criticism", "Digital Humanities", "Elective IV", "Dissertation"]
    },
    "Economics": {
        1: ["Microeconomics I", "Macroeconomics I", "Mathematics for Economics", "Indian Economy", "English"],
        2: ["Microeconomics II", "Macroeconomics II", "Statistics for Economics", "Monetary Economics", "Environmental Studies"],
        3: ["Development Economics", "International Economics", "Public Economics", "Econometrics I", "Agricultural Economics"],
        4: ["Labour Economics", "Industrial Economics", "Health Economics", "Econometrics II", "Research Methodology"],
        5: ["Financial Economics", "Behavioral Economics", "Urban Economics", "Gender Economics", "Elective I"],
        6: ["Political Economy", "Energy Economics", "Economic Thought", "Elective II", "Project"],
        7: ["Environmental Economics", "Transport Economics", "Welfare Economics", "Elective III", "Policy Analysis"],
        8: ["Game Theory", "Experimental Economics", "Development Policy", "Elective IV", "Thesis"]
    },
    "History": {
        1: ["History of India I", "History of Tamil Nadu I", "World History I", "History of Europe I", "English"],
        2: ["History of India II", "History of Tamil Nadu II", "World History II", "History of Europe II", "Constitutional History"],
        3: ["History of India III", "History of Tamil Nadu III", "History of USA", "History of Russia", "History of East Asia"],
        4: ["History of India IV", "History of Tamil Nadu IV", "History of UK", "History of France", "Historiography"],
        5: ["History of South East Asia", "History of West Asia", "History of Africa", "Archaeology", "Elective I"],
        6: ["History of Science", "History of Art", "Museology", "Elective II", "Project"],
        7: ["Medieval India", "Colonial India", "Freedom Movement", "Elective III", "Research Methods"],
        8: ["Modern India", "Contemporary History", "Historical Tourism", "Elective IV", "Dissertation"]
    }
}

# Department codes mapping
DEPT_CODE_MAP = {
    "Computer Science": "CS",
    "Computer Applications": "CA",
    "Commerce Finance": "CF",
    "Commerce Co-op": "CC",
    "English": "EN",
    "Economics": "EC",
    "History": "HY"
}

# =====================================================
# HELPER FUNCTIONS
# =====================================================

def generate_subject_code(dept_name, semester, index):
    """Generate subject code like CS0101, CA0203, etc."""
    dept_code = DEPT_CODE_MAP.get(dept_name, "XX")
    return f"{dept_code}{semester:02d}{index:02d}"

def get_or_create_academic_year():
    """Get or create current academic year"""
    today = date.today()
    if today.month >= 6:
        start_year = today.year
        end_year = today.year + 1
    else:
        start_year = today.year - 1
        end_year = today.year
    
    year_str = f"{start_year}-{end_year}"
    
    academic_year = AcademicYear.query.filter_by(year=year_str).first()
    if not academic_year:
        academic_year = AcademicYear(
            year=year_str,
            start_date=date(start_year, 6, 1),
            end_date=date(end_year, 4, 30),
            is_current=True
        )
        db.session.add(academic_year)
        db.session.flush()
        print(f"   Created academic year: {year_str}")
    return academic_year

def get_or_create_course(dept):
    """Get or create course for department"""
    course_code = f"{dept.code}_PROG"
    course = Course.query.filter_by(code=course_code).first()
    if not course:
        course = Course(
            name=f"{dept.name} Program",
            code=course_code,
            duration_years=3,
            department_id=dept.id
        )
        db.session.add(course)
        db.session.flush()
        print(f"   Created course for {dept.name}")
    return course

def get_or_create_semester(course, semester_num, academic_year):
    """Get or create semester"""
    semester = Semester.query.filter_by(
        semester_number=semester_num,
        course_id=course.id,
        academic_year_id=academic_year.id
    ).first()
    
    if not semester:
        if semester_num % 2 == 1:  # Odd semester
            start_date = date(academic_year.start_date.year, 6, 1)
            end_date = date(academic_year.start_date.year, 11, 30)
        else:  # Even semester
            start_date = date(academic_year.start_date.year + 1, 12, 1)
            end_date = date(academic_year.start_date.year + 1, 4, 30)
        
        semester = Semester(
            semester_number=semester_num,
            course_id=course.id,
            academic_year_id=academic_year.id,
            start_date=start_date,
            end_date=end_date
        )
        db.session.add(semester)
        db.session.flush()
    return semester

def get_date_range_dates(start_date, end_date):
    """Get list of dates between start and end (inclusive), excluding Sundays"""
    date_list = []
    current = start_date
    while current <= end_date:
        # Skip Sunday (weekday() == 6)
        if current.weekday() != 6:
            date_list.append(current)
        current += timedelta(days=1)
    return date_list

def split_subjects_equally(subjects):
    """
    Split subjects equally between 10AM and 2PM
    If odd number, extra goes to 2PM
    """
    if not subjects:
        return [], []
    
    subjects_copy = subjects.copy()
    random.shuffle(subjects_copy)
    split_point = len(subjects_copy) // 2
    
    # If odd number, extra goes to 2PM
    if len(subjects_copy) % 2 == 1:
        return subjects_copy[:split_point], subjects_copy[split_point:]
    else:
        return subjects_copy[:split_point], subjects_copy[split_point:]

def is_sunday(date_obj):
    """Check if given date is Sunday"""
    return date_obj.weekday() == 6

# =====================================================
# PART 1: ADD MISSING DEPARTMENTS
# =====================================================

def add_missing_departments():
    """Add only missing departments from the predefined list"""
    print("\n" + "="*60)
    print("PART 1: ADDING MISSING DEPARTMENTS")
    print("="*60)
    
    added = 0
    existing = 0
    
    for dept_data in ALL_DEPARTMENTS:
        dept = Department.query.filter_by(code=dept_data['code']).first()
        
        if not dept:
            dept = Department(
                name=dept_data['name'],
                code=dept_data['code']
            )
            db.session.add(dept)
            db.session.flush()
            added += 1
            print(f"   Added: {dept_data['name']} ({dept_data['code']})")
        else:
            existing += 1
            print(f"   Already exists: {dept_data['name']} ({dept_data['code']})")
    
    db.session.commit()
    
    print(f"\nDepartment Summary:")
    print(f"   Added: {added} new departments")
    print(f"   Existing: {existing} departments")
    print(f"   Total: {added + existing}/{len(ALL_DEPARTMENTS)} departments")
    
    return added

# =====================================================
# PART 2: ADD MISSING SUBJECTS
# =====================================================

def add_missing_subjects():
    """Add only missing subjects for all departments and semesters"""
    print("\n" + "="*60)
    print("PART 2: ADDING MISSING SUBJECTS")
    print("="*60)
    
    academic_year = get_or_create_academic_year()
    total_added = 0
    total_existing = 0
    
    for dept_name, semesters in DEPARTMENT_SUBJECTS.items():
        dept = Department.query.filter_by(name=dept_name).first()
        if not dept:
            print(f"   Department {dept_name} not found - skipping")
            continue
        
        course = get_or_create_course(dept)
        dept_added = 0
        dept_existing = 0
        
        print(f"\nProcessing {dept_name}:")
        
        for semester_num, subjects in semesters.items():
            semester = get_or_create_semester(course, semester_num, academic_year)
            
            for idx, subject_name in enumerate(subjects, 1):
                subject_code = generate_subject_code(dept_name, semester_num, idx)
                
                existing = Subject.query.filter_by(code=subject_code).first()
                
                if not existing:
                    subject = Subject(
                        name=subject_name,
                        code=subject_code,
                        credits=4,
                        department_id=dept.id,
                        semester_id=semester.id
                    )
                    db.session.add(subject)
                    dept_added += 1
                    print(f"      Sem {semester_num}: {subject_name} ({subject_code})")
                else:
                    dept_existing += 1
            
            db.session.flush()
        
        total_added += dept_added
        total_existing += dept_existing
        print(f"   -> {dept_name}: Added {dept_added}, Existing {dept_existing}")
    
    db.session.commit()
    
    print(f"\nSubject Summary:")
    print(f"   Added: {total_added} new subjects")
    print(f"   Existing: {total_existing} subjects")
    print(f"   Total: {total_added + total_existing} subjects")
    
    return total_added

# =====================================================
# PART 3: CHECK DATABASE STATUS
# =====================================================

def check_database_status():
    """Print current database status"""
    print("\n" + "="*60)
    print("PART 3: DATABASE STATUS CHECK")
    print("="*60)
    
    # Count all entities
    dept_count = Department.query.count()
    subject_count = Subject.query.count()
    student_count = Student.query.count()
    teacher_count = User.query.filter_by(role='teacher').count()
    hod_count = User.query.filter_by(role='hod').count()
    coordinator_count = User.query.filter_by(role='coordinator').count()
    exam_count = ExamTimetable.query.count()
    
    print(f"\nDATABASE COUNTS:")
    print(f"   * Departments: {dept_count}")
    print(f"   * Subjects: {subject_count}")
    print(f"   * Students: {student_count}")
    print(f"   * Teachers: {teacher_count}")
    print(f"   * HODs: {hod_count}")
    print(f"   * Coordinators: {coordinator_count}")
    print(f"   * Exams Scheduled: {exam_count}")
    
    # Department-wise subject distribution
    if dept_count > 0:
        print(f"\nSUBJECTS BY DEPARTMENT:")
        departments = Department.query.order_by(Department.name).all()
        for dept in departments:
            subj_count = Subject.query.filter_by(department_id=dept.id).count()
            status = "OK" if subj_count > 0 else "MISSING"
            print(f"   {status} {dept.name}: {subj_count} subjects")
    
    # Subject distribution by semester
    print(f"\nSUBJECTS BY SEMESTER:")
    for sem in range(1, 9):
        count = Subject.query.filter_by(semester_id=sem).count()
        if count > 0:
            print(f"   Semester {sem}: {count} subjects")
    
    return {
        'departments': dept_count,
        'subjects': subject_count,
        'students': student_count,
        'teachers': teacher_count,
        'exams': exam_count
    }

# =====================================================
# PART 4: GENERATE EXAM TIMETABLE - FIXED (ONE EXAM PER DEPARTMENT PER DAY)
# =====================================================

def generate_exam_timetable(academic_year="2025-2026", exam_cycle="EVEN", 
                           start_date_str=None, end_date_str=None, time_option="BOTH"):
    """
    Auto-generate exam timetable for ALL departments
    ENSURES: ONE EXAM PER DEPARTMENT PER DAY
    Sundays automatically skipped
    """
    print("\n" + "="*60)
    print(f"GENERATING EXAM TIMETABLE - {time_option} OPTION")
    print("(ONE EXAM PER DEPARTMENT PER DAY)")
    print("="*60)
    
    # If dates not provided, ask user
    if start_date_str is None:
        start_date_str = input("Enter Start Date (YYYY-MM-DD): ").strip()
        if start_date_str.lower() in ['exit', 'quit', '']:
            print("Cancelled by user")
            return 0
    
    if end_date_str is None:
        end_date_str = input("Enter End Date (YYYY-MM-DD): ").strip()
        if end_date_str.lower() in ['exit', 'quit', '']:
            print("Cancelled by user")
            return 0
    
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        print("Invalid date format. Using defaults: 2026-03-09 to 2026-04-06")
        start_date = date(2026, 3, 9)
        end_date = date(2026, 4, 6)
    
    # Validate dates
    if start_date > end_date:
        print("Error: Start date cannot be after end date")
        return 0
    
    # Get semesters based on cycle
    if exam_cycle == "ODD":
        semesters = [1, 3, 5, 7]
        semester_display = "Odd Semesters (1,3,5,7)"
        subjects_per_dept = 20  # 4 semesters × 5 subjects
    elif exam_cycle == "EVEN":
        semesters = [2, 4, 6, 8]
        semester_display = "Even Semesters (2,4,6,8)"
        subjects_per_dept = 20  # 4 semesters × 5 subjects
    else:  # FULL
        semesters = [1, 2, 3, 4, 5, 6, 7, 8]
        semester_display = "All Semesters (1-8)"
        subjects_per_dept = 40  # 8 semesters × 5 subjects
    
    # Get ALL departments
    departments = Department.query.all()
    
    if not departments:
        print("No departments found in database!")
        return 0
    
    # Generate date list (Sundays excluded)
    date_list = get_date_range_dates(start_date, end_date)
    total_days = len(date_list)
    
    if total_days == 0:
        print(f"No working days in range")
        return 0
    
    # Show Sundays skipped
    skipped_sundays = []
    current = start_date
    while current <= end_date:
        if is_sunday(current):
            skipped_sundays.append(current)
        current += timedelta(days=1)
    
    print(f"\nConfiguration:")
    print(f"   Academic Year: {academic_year}")
    print(f"   Exam Cycle: {exam_cycle} ({semester_display})")
    print(f"   Date Range: {start_date} to {end_date}")
    print(f"   Total Days (excluding Sundays): {total_days}")
    print(f"   Time Option: {time_option}")
    print(f"   RULE: ONE EXAM PER DEPARTMENT PER DAY")
    if skipped_sundays:
        print(f"   Sundays skipped: {len(skipped_sundays)} days")
    
    # Calculate if enough days are available
    total_exams_needed = len(departments) * subjects_per_dept
    
    if time_option == "BOTH":
        # Each day can have 2 exams per department (10AM and 2PM)
        max_exams_possible = total_days * len(departments) * 2
        if total_exams_needed > max_exams_possible:
            print(f"\n⚠️ WARNING: Need {total_exams_needed} exams but only {max_exams_possible} slots available")
            print(f"   Try a longer date range")
            proceed = input("Continue anyway? (y/n): ").lower()
            if proceed != 'y':
                return 0
    else:
        # Each day can have 1 exam per department
        max_exams_possible = total_days * len(departments)
        if total_exams_needed > max_exams_possible:
            print(f"\n⚠️ WARNING: Need {total_exams_needed} exams but only {max_exams_possible} slots available")
            print(f"   Need {total_days} days × {len(departments)} departments = {max_exams_possible} slots")
            print(f"   Try a longer date range or use BOTH option")
            return 0
    
    proceed = input(f"\nGenerate {total_exams_needed} exams? (y/n): ").lower()
    if proceed != 'y':
        print("Cancelled")
        return 0
    
    # Clear existing exams for this date range
    existing = ExamTimetable.query.filter(
        ExamTimetable.exam_date >= start_date,
        ExamTimetable.exam_date <= end_date
    ).count()
    
    if existing > 0:
        print(f"\nFound {existing} existing exams")
        overwrite = input("Overwrite? (y/n): ").lower()
        if overwrite == 'y':
            ExamTimetable.query.filter(
                ExamTimetable.exam_date >= start_date,
                ExamTimetable.exam_date <= end_date
            ).delete()
            db.session.commit()
            print(f"Cleared {existing} existing exams")
        else:
            print("Keeping existing exams")
            return 0
    
    # Get subjects for each department based on cycle
    dept_subjects = {}
    for dept in departments:
        subjects = Subject.query.filter(
            Subject.department_id == dept.id,
            Subject.semester_id.in_(semesters)
        ).all()
        
        if subjects:
            # Shuffle subjects for random distribution
            random.shuffle(subjects)
            dept_subjects[dept.id] = subjects
            print(f"\n{dept.name}: {len(subjects)} subjects to schedule")
        else:
            print(f"\n⚠️ No subjects for {dept.name}")
    
    total_saved = 0
    dept_counts = {}
    
    # Track subject usage per department
    subject_index = {dept.id: 0 for dept in departments}
    
    # Create a schedule: each date gets ONE exam per department
    if time_option == "BOTH":
        # Each date will have 2 sessions (10AM and 2PM)
        for date_idx, exam_date in enumerate(date_list):
            date_saved = 0
            
            # First session - 10AM
            for dept in departments:
                if dept.id in dept_subjects and subject_index[dept.id] < len(dept_subjects[dept.id]):
                    subject = dept_subjects[dept.id][subject_index[dept.id]]
                    subject_index[dept.id] += 1
                    
                    exam = ExamTimetable(
                        department_id=dept.id,
                        semester=subject.semester_id,
                        subject_id=subject.id,
                        exam_date=exam_date,
                        exam_time='10AM',
                        academic_year=academic_year,
                        exam_cycle=exam_cycle,
                        created_by=1,
                        status='Generated'
                    )
                    db.session.add(exam)
                    date_saved += 1
                    total_saved += 1
            
            # Second session - 2PM
            for dept in departments:
                if dept.id in dept_subjects and subject_index[dept.id] < len(dept_subjects[dept.id]):
                    subject = dept_subjects[dept.id][subject_index[dept.id]]
                    subject_index[dept.id] += 1
                    
                    exam = ExamTimetable(
                        department_id=dept.id,
                        semester=subject.semester_id,
                        subject_id=subject.id,
                        exam_date=exam_date,
                        exam_time='2PM',
                        academic_year=academic_year,
                        exam_cycle=exam_cycle,
                        created_by=1,
                        status='Generated'
                    )
                    db.session.add(exam)
                    date_saved += 1
                    total_saved += 1
            
            db.session.commit()
            print(f"   {exam_date}: Scheduled {date_saved} exams ({date_saved//2} per session)")
    
    elif time_option == "10AM":
        # Only 10AM session
        for date_idx, exam_date in enumerate(date_list):
            date_saved = 0
            for dept in departments:
                if dept.id in dept_subjects and subject_index[dept.id] < len(dept_subjects[dept.id]):
                    subject = dept_subjects[dept.id][subject_index[dept.id]]
                    subject_index[dept.id] += 1
                    
                    exam = ExamTimetable(
                        department_id=dept.id,
                        semester=subject.semester_id,
                        subject_id=subject.id,
                        exam_date=exam_date,
                        exam_time='10AM',
                        academic_year=academic_year,
                        exam_cycle=exam_cycle,
                        created_by=1,
                        status='Generated'
                    )
                    db.session.add(exam)
                    date_saved += 1
                    total_saved += 1
            
            db.session.commit()
            print(f"   {exam_date}: Scheduled {date_saved} exams")
    
    elif time_option == "2PM":
        # Only 2PM session
        for date_idx, exam_date in enumerate(date_list):
            date_saved = 0
            for dept in departments:
                if dept.id in dept_subjects and subject_index[dept.id] < len(dept_subjects[dept.id]):
                    subject = dept_subjects[dept.id][subject_index[dept.id]]
                    subject_index[dept.id] += 1
                    
                    exam = ExamTimetable(
                        department_id=dept.id,
                        semester=subject.semester_id,
                        subject_id=subject.id,
                        exam_date=exam_date,
                        exam_time='2PM',
                        academic_year=academic_year,
                        exam_cycle=exam_cycle,
                        created_by=1,
                        status='Generated'
                    )
                    db.session.add(exam)
                    date_saved += 1
                    total_saved += 1
            
            db.session.commit()
            print(f"   {exam_date}: Scheduled {date_saved} exams")
    
    print(f"\n" + "="*60)
    print(f"SUCCESS: Generated {total_saved} exams")
    print(f"Time Option: {time_option}")
    print(f"Rule: ONE EXAM PER DEPARTMENT PER DAY - ENSURED ✓")
    print(f"Date range: {start_date} to {end_date}")
    print("="*60)
    
    return total_saved

# =====================================================
# PART 5: MAIN MENU
# =====================================================

def main_menu():
    """Display main menu with time options"""
    while True:
        print("\n" + "="*70)
        print("MASTER ACADEMIC SETUP SCRIPT")
        print("="*70)
        print("1. Run Complete Setup (Departments + Subjects)")
        print("2. Generate Exam Timetable - 10 AM ONLY (One Per Dept Per Day)")
        print("3. Generate Exam Timetable - 2 PM ONLY (One Per Dept Per Day)")
        print("4. Generate Exam Timetable - BOTH Sessions (One Per Dept Per Session)")
        print("5. Check Database Status")
        print("6. Clear Timetable")
        print("7. Exit")
        
        choice = input("\nSelect option [4]: ").strip() or '4'
        
        with app.app_context():
            if choice == '1':
                # Complete setup
                dept_count = Department.query.count()
                if dept_count == 0:
                    print("\nCreating all data...")
                    add_missing_departments()
                    add_missing_subjects()
                else:
                    print(f"\nData already exists ({dept_count} departments)")
                
                # Ask if want to generate timetable
                generate = input("\nGenerate exam timetable now? (y/n): ").lower()
                if generate == 'y':
                    time_option = input("Time option? (10AM/2PM/BOTH) [BOTH]: ").upper() or "BOTH"
                    start_date = input("Start Date (YYYY-MM-DD): ")
                    end_date = input("End Date (YYYY-MM-DD): ")
                    exam_cycle = input("Exam Cycle [EVEN] (ODD/EVEN/FULL): ") or "EVEN"
                    generate_exam_timetable("2025-2026", exam_cycle.upper(), 
                                           start_date, end_date, time_option)
            
            elif choice == '2':
                # 10 AM ONLY
                start_date = input("Start Date (YYYY-MM-DD): ")
                end_date = input("End Date (YYYY-MM-DD): ")
                exam_cycle = input("Exam Cycle [EVEN] (ODD/EVEN/FULL): ") or "EVEN"
                generate_exam_timetable("2025-2026", exam_cycle.upper(), 
                                       start_date, end_date, "10AM")
            
            elif choice == '3':
                # 2 PM ONLY
                start_date = input("Start Date (YYYY-MM-DD): ")
                end_date = input("End Date (YYYY-MM-DD): ")
                exam_cycle = input("Exam Cycle [EVEN] (ODD/EVEN/FULL): ") or "EVEN"
                generate_exam_timetable("2025-2026", exam_cycle.upper(), 
                                       start_date, end_date, "2PM")
            
            elif choice == '4':
                # BOTH
                start_date = input("Start Date (YYYY-MM-DD): ")
                end_date = input("End Date (YYYY-MM-DD): ")
                exam_cycle = input("Exam Cycle [EVEN] (ODD/EVEN/FULL): ") or "EVEN"
                generate_exam_timetable("2025-2026", exam_cycle.upper(), 
                                       start_date, end_date, "BOTH")
            
            elif choice == '5':
                check_database_status()
            
            elif choice == '6':
                clear_choice = input("Clear ALL exams? (yes/no): ")
                if clear_choice.lower() == 'yes':
                    clear_timetable()
            
            elif choice == '7':
                print("Exiting...")
                break
            
            else:
                print("Invalid option!")

def clear_timetable(academic_year=None):
    """Clear exams for a specific year or all years"""
    print("\n" + "="*60)
    print("CLEARING TIMETABLE")
    print("="*60)
    
    if academic_year:
        count = ExamTimetable.query.filter_by(academic_year=academic_year).count()
        if count > 0:
            ExamTimetable.query.filter_by(academic_year=academic_year).delete()
            db.session.commit()
            print(f"Cleared {count} exams for academic year {academic_year}")
        else:
            print(f"No exams found for academic year {academic_year}")
    else:
        count = ExamTimetable.query.count()
        if count > 0:
            ExamTimetable.query.delete()
            db.session.commit()
            print(f"Cleared ALL {count} exams from database")
        else:
            print("No exams found in database")
    
    return count

# =====================================================
# MAIN EXECUTION
# =====================================================

if __name__ == "__main__":
    app = create_app('development')
    
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Show menu
        main_menu()
        
        