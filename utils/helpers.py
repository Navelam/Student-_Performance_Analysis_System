# utils/helpers.py
"""
Helper functions for Student Performance Analysis System
"""

import random
import string
from datetime import datetime, date

# =====================================================
# DEPARTMENT DEFINITIONS
# =====================================================

# Department structure with semesters and subjects
DEPARTMENTS = {
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

# Department codes for registration numbers
DEPT_CODES = {
    "Computer Science": "CS",
    "Computer Applications": "CA",
    "Commerce Finance": "CF",
    "Commerce Co-op": "CC",
    "English": "EN",
    "Economics": "EC",
    "History": "HY"
}

# Batch mapping (Year -> Batch Year)
BATCH_MAPPING = {
    1: 2025,  # 1st Year -> 2025 batch
    2: 2024,  # 2nd Year -> 2024 batch
    3: 2023,  # 3rd Year -> 2023 batch
    4: 2022   # 4th Year -> 2022 batch
}

# Semester to Year mapping
SEMESTER_TO_YEAR = {
    1: 1, 2: 1,   # Sem 1-2: Year 1
    3: 2, 4: 2,   # Sem 3-4: Year 2
    5: 3, 6: 3,   # Sem 5-6: Year 3
    7: 4, 8: 4    # Sem 7-8: Year 4
}

# =====================================================
# HELPER FUNCTIONS
# =====================================================

def get_current_semester():
    """Determine current semester based on date"""
    today = date.today()
    month = today.month
    
    # June to December -> Odd semester (1,3,5,7)
    if 6 <= month <= 12:
        return 1  # Odd semester
    # January to April -> Even semester (2,4,6,8)
    else:
        return 2  # Even semester

def get_semester_number(year, is_odd=True):
    """
    Get semester number based on year and odd/even
    
    Args:
        year: 1,2,3,4
        is_odd: True for odd semester, False for even
    
    Returns:
        semester_number: 1-8
    """
    base = (year - 1) * 2
    return base + (1 if is_odd else 2)

def get_year_from_semester(semester):
    """Get academic year (1-4) from semester number (1-8)"""
    return SEMESTER_TO_YEAR.get(semester, 1)

def get_batch_from_year(year):
    """Get batch year from academic year"""
    return BATCH_MAPPING.get(year, 2025)

def get_current_academic_year():
    """Get current academic year as string"""
    today = date.today()
    if today.month >= 6:
        return f"{today.year}-{today.year + 1}"
    else:
        return f"{today.year - 1}-{today.year}"

def generate_registration_number(department_name, batch_year, sequence):
    """
    Generate a unique registration number for a student
    
    Format: [DEPT_CODE][BATCH_YEAR][3-DIGIT SEQUENCE]
    Example: CS2025001 for Computer Science student in 2025 batch
    """
    dept_code = DEPT_CODES.get(department_name, "XX")
    reg_number = f"{dept_code}{batch_year}{sequence:03d}"
    return reg_number

def generate_student_id(department_name, batch_year, sequence):
    """
    Generate a unique student ID
    
    Format: [DEPT_CODE][BATCH_YEAR][3-DIGIT SEQUENCE]
    Example: CS2025001 for Computer Science student
    """
    dept_code = DEPT_CODES.get(department_name, "XX")
    student_id = f"{dept_code}{batch_year}{sequence:03d}"
    return student_id

def get_all_subjects():
    """Get all subjects with their metadata"""
    all_subjects = []
    for dept_name, semesters in DEPARTMENTS.items():
        for semester_num, subjects in semesters.items():
            for idx, subject_name in enumerate(subjects, 1):
                subject_code = f"{DEPT_CODES[dept_name]}{semester_num:02d}{idx:02d}"
                all_subjects.append({
                    'name': subject_name,
                    'code': subject_code,
                    'department': dept_name,
                    'semester': semester_num,
                    'year': get_year_from_semester(semester_num),
                    'credits': 4
                })
    return all_subjects

def get_subjects_by_department_semester(department, semester):
    """Get subjects for a department and semester"""
    if department in DEPARTMENTS and semester in DEPARTMENTS[department]:
        return DEPARTMENTS[department][semester]
    return []

def get_all_departments():
    """Get list of all departments"""
    return list(DEPARTMENTS.keys())

def get_semesters_for_year(year):
    """Get semester numbers for a given academic year"""
    start_sem = (year - 1) * 2 + 1
    return [start_sem, start_sem + 1]

def calculate_risk_status(attendance, final_internal):
    """
    Calculate risk status based on attendance and marks
    
    Rules:
    - Attendance < 70% → Critical
    - Final Internal < 10 → High Risk
    - Final Internal < 15 → Average
    - Otherwise → Safe
    """
    if attendance < 70:
        return "Critical"
    elif final_internal < 10:
        return "High Risk"
    elif final_internal < 15:
        return "Average"
    else:
        return "Safe"

def calculate_final_internal(internal1, internal2, seminar, assessment):
    """
    Calculate final internal marks (out of 25)
    
    Formula: (internal1 + internal2 + seminar + assessment) / 2
    """
    total = internal1 + internal2 + seminar + assessment
    final_internal = total / 2
    return round(final_internal, 2)

def generate_password(length=8):
    """Generate a random password"""
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def format_phone_number(phone):
    """Format phone number to standard format"""
    if not phone:
        return None
    # Remove any non-digit characters
    phone = ''.join(filter(str.isdigit, phone))
    if len(phone) == 10:
        return f"{phone[:3]}-{phone[3:6]}-{phone[6:]}"
    return phone
def get_academic_year_and_semester():
    """Get current academic year and active semester (for backward compatibility)"""
    from model import AcademicYear
    from extensions import db
    
    today = date.today()
    
    # Determine academic year (June to April)
    if today.month >= 6:
        current_year = today.year
        next_year = today.year + 1
    else:
        current_year = today.year - 1
        next_year = today.year
    
    year_str = f"{current_year}-{next_year}"
    
    # Get or create academic year
    academic_year = AcademicYear.query.filter_by(year=year_str).first()
    if not academic_year:
        academic_year = AcademicYear(
            year=year_str,
            start_date=date(current_year, 6, 1),
            end_date=date(next_year, 4, 30),
            is_current=True
        )
        db.session.add(academic_year)
        db.session.flush()
    
    # Determine active semester
    if today.month <= 11:  # June to November -> Odd semester
        active_semester = 1
    else:  # December to April -> Even semester
        active_semester = 2
    
    return {
        "academic_year": year_str,
        "active_semester": active_semester,
        "academic_year_obj": academic_year
    }
def get_subjects(department, semester):
    """Get subjects for a department and semester (for backward compatibility)"""
    if department in DEPARTMENTS and semester in DEPARTMENTS[department]:
        return DEPARTMENTS[department][semester]
    return []