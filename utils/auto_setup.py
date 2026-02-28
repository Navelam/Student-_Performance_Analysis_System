# utils/auto_setup.py
"""
Auto Setup Script for Student Performance Analysis System
Creates academic years, batches, semesters, subjects, and students
Department-based student name generation - does NOT overwrite existing names
"""

import sys
import re
from pathlib import Path
from datetime import datetime, date
from werkzeug.security import generate_password_hash

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from extensions import db
from model import (
    User, Department, Course, AcademicYear, Semester, 
    Subject, Student, TeacherSubject, Notification,
    StudentPerformance, Attendance
)

# Import from helpers using correct function names
from utils.helpers import (
    DEPARTMENTS,
    DEPT_CODES,
    BATCH_MAPPING,
    SEMESTER_TO_YEAR,
    get_current_semester,
    get_semester_number,
    get_year_from_semester,
    get_batch_from_year,
    get_current_academic_year,
    get_all_subjects,
    get_subjects_by_department_semester,
    get_all_departments,
    get_semesters_for_year,
    generate_registration_number,
    generate_student_id,
    generate_password
)

# Configuration
STUDENT_PASSWORD = "1234"
TEACHER_PASSWORD = "123"
HOD_PASSWORD = "hod123"
COORDINATOR_PASSWORD = "coord123"
PRINCIPAL_PASSWORD = "123"

# Student distribution - 15 students per semester (120 per department)
STUDENTS_PER_SEMESTER = 15
TOTAL_STUDENTS_PER_DEPT = STUDENTS_PER_SEMESTER * 8  # 120 students per department

class AcademicAutoSetup:
    """Automated academic setup manager"""
    
    def __init__(self, app):
        self.app = app
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.academic_year_str = get_current_academic_year()
        self.current_semester_type = get_current_semester()  # 1 for odd, 2 for even
        self.departments = {}
        self.courses = {}
        self.academic_year_obj = None
        self.semesters = []
        self.subjects = []
        
    def setup_all(self):
        """Run complete academic setup"""
        print("\n" + "=" * 60)
        print("ACADEMIC AUTO SETUP")
        print("=" * 60)
        print(f"Academic Year: {self.academic_year_str}")
        print(f"Current Semester Type: {'Odd' if self.current_semester_type == 1 else 'Even'}")
        print("=" * 60)
        
        with self.app.app_context():
            # Step 1: Create Academic Year
            self.create_academic_year()
            
            # Step 2: Create Departments
            self.create_departments()
            
            # Step 3: Create Courses
            self.create_courses()
            
            # Step 4: Create Semesters
            self.create_semesters()
            
            # Step 5: Create Subjects
            self.create_subjects()
            
            # Step 6: Create Principal
            self.create_principal()
            
            # Step 7: Create HODs
            self.create_hods()
            
            # Step 8: Create Coordinators
            self.create_coordinators()
            
            # Step 9: Create Teachers (6 per department)
            self.create_teachers()
            
            # Step 10: Create Students (120 per department - 15 per semester)
            self.create_all_students()
            
            # Step 11: Verify setup
            self.verify_setup()
            
            # Commit all changes
            db.session.commit()
        
        print("\n" + "=" * 60)
        print("ACADEMIC AUTO SETUP COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    def create_academic_year(self):
        """Create academic year 2025-2026"""
        print("\n1. Creating Academic Year...")
        
        # Parse academic year
        start_year = int(self.academic_year_str.split('-')[0])
        end_year = int(self.academic_year_str.split('-')[1])
        
        # Check if exists
        academic_year = AcademicYear.query.filter_by(year=self.academic_year_str).first()
        
        if not academic_year:
            academic_year = AcademicYear(
                year=self.academic_year_str,
                start_date=date(start_year, 6, 1),
                end_date=date(end_year, 4, 30),
                is_current=True
            )
            db.session.add(academic_year)
            db.session.flush()
            print(f"   - Created academic year: {self.academic_year_str}")
        else:
            print(f"   - Academic year {self.academic_year_str} already exists")
            
        self.academic_year_obj = academic_year
        return academic_year
    
    def create_departments(self):
        """Create all departments"""
        print("\n2. Creating Departments...")
        
        dept_list = get_all_departments()
        
        for dept_name in dept_list:
            dept_code = DEPT_CODES.get(dept_name, dept_name[:2].upper())
            
            department = Department.query.filter_by(code=dept_code).first()
            
            if not department:
                department = Department(
                    code=dept_code,
                    name=dept_name
                )
                db.session.add(department)
                db.session.flush()
                print(f"   - Created department: {dept_name} ({dept_code})")
            else:
                print(f"   - Department {dept_name} already exists")
                
            self.departments[dept_name] = department
            
        return self.departments
    
    def create_courses(self):
        """Create courses for each department"""
        print("\n3. Creating Courses...")
        
        course_data = [
            ("Computer Science", "B.Sc Computer Science", "BSC_CS", 3),
            ("Computer Applications", "BCA", "BCA", 3),
            ("Commerce Finance", "B.Com Finance", "BCOM_FIN", 3),
            ("Commerce Co-op", "B.Com Co-op", "BCOM_COOP", 3),
            ("English", "B.A English", "BA_ENG", 3),
            ("Economics", "B.A Economics", "BA_ECO", 3),
            ("History", "B.A History", "BA_HIS", 3)
        ]
        
        for dept_name, course_name, course_code, duration in course_data:
            department = self.departments.get(dept_name)
            if not department:
                continue
                
            course = Course.query.filter_by(code=course_code).first()
            
            if not course:
                course = Course(
                    name=course_name,
                    code=course_code,
                    duration_years=duration,
                    department_id=department.id
                )
                db.session.add(course)
                db.session.flush()
                print(f"   - Created course: {course_name} for {dept_name}")
            else:
                print(f"   - Course {course_name} already exists")
                
            self.courses[dept_name] = course
            
        return self.courses
    
    def create_semesters(self):
        """Create all semesters 1-8 for all courses"""
        print("\n4. Creating Semesters...")
        
        semesters_created = 0
        
        for dept_name, course in self.courses.items():
            for sem_num in range(1, 9):  # 8 semesters for 4-year course
                # Check if semester exists
                semester = Semester.query.filter_by(
                    semester_number=sem_num,
                    course_id=course.id,
                    academic_year_id=self.academic_year_obj.id
                ).first()
                
                if not semester:
                    # Calculate dates based on semester
                    if sem_num % 2 == 1:  # Odd semester
                        start_date = date(self.academic_year_obj.start_date.year, 6, 1)
                        end_date = date(self.academic_year_obj.start_date.year, 11, 30)
                    else:  # Even semester
                        start_date = date(self.academic_year_obj.start_date.year + 1, 12, 1)
                        end_date = date(self.academic_year_obj.start_date.year + 1, 4, 30)
                    
                    semester = Semester(
                        semester_number=sem_num,
                        course_id=course.id,
                        academic_year_id=self.academic_year_obj.id,
                        start_date=start_date,
                        end_date=end_date
                    )
                    db.session.add(semester)
                    semesters_created += 1
                    print(f"   Created Semester {sem_num} for {dept_name}")
                    
                self.semesters.append(semester)
        
        db.session.flush()
        print(f"   - Created {semesters_created} new semesters")
        print(f"   - Total semesters: {len(self.semesters)}")
        
        return self.semesters
    
    def create_subjects(self):
        """Create all subjects for all semesters 1-8"""
        print("\n5. Creating Subjects...")
        
        subjects_created = 0
        all_subjects = get_all_subjects()  # Gets all subjects from helpers.py including sem 1-8
        
        # Create a mapping of semester by department and semester number
        semester_map = {}
        for semester in self.semesters:
            course = Course.query.get(semester.course_id)
            if course:
                dept = Department.query.get(course.department_id)
                if dept:
                    key = (dept.name, semester.semester_number)
                    semester_map[key] = semester
        
        # Create subjects for all semesters 1-8
        for subject_info in all_subjects:
            dept_name = subject_info['department']
            dept = self.departments.get(dept_name)
            
            if not dept:
                continue
                
            semester_num = subject_info['semester']
            key = (dept_name, semester_num)
            semester = semester_map.get(key)
            
            if not semester:
                # If semester doesn't exist, create it
                print(f"   Creating missing Semester {semester_num} for {dept_name}...")
                course = self.courses.get(dept_name)
                if course:
                    if semester_num % 2 == 1:  # Odd semester
                        start_date = date(self.academic_year_obj.start_date.year, 6, 1)
                        end_date = date(self.academic_year_obj.start_date.year, 11, 30)
                    else:  # Even semester
                        start_date = date(self.academic_year_obj.start_date.year + 1, 12, 1)
                        end_date = date(self.academic_year_obj.start_date.year + 1, 4, 30)
                    
                    semester = Semester(
                        semester_number=semester_num,
                        course_id=course.id,
                        academic_year_id=self.academic_year_obj.id,
                        start_date=start_date,
                        end_date=end_date
                    )
                    db.session.add(semester)
                    db.session.flush()
                    semester_map[key] = semester
                    print(f"   Created Semester {semester_num}")
            
            # Check if subject exists
            subject = Subject.query.filter_by(
                code=subject_info['code']
            ).first()
            
            if not subject:
                subject = Subject(
                    name=subject_info['name'],
                    code=subject_info['code'],
                    credits=subject_info['credits'],
                    department_id=dept.id,
                    semester_id=semester.id
                )
                db.session.add(subject)
                subjects_created += 1
                print(f"   Created: {subject_info['code']} - {subject_info['name']} (Sem {semester_num})")
        
        db.session.flush()
        print(f"   - Created {subjects_created} new subjects")
        
        # Count total subjects
        total_subjects = Subject.query.count()
        print(f"   - Total subjects in database: {total_subjects}")
        
        return self.subjects
    
    def create_principal(self):
        """Create principal user"""
        print("\n6. Creating Principal...")
        
        principal = User.query.filter_by(role='principal').first()
        
        if not principal:
            principal = User(
                username="principal",
                email="principal@education.com",
                full_name="Dr. Rajesh Kumar",
                role="principal",
                department=None,  # FIXED: Principal has no department
                password_hash=generate_password_hash(PRINCIPAL_PASSWORD),
                is_active=True
            )
            db.session.add(principal)
            db.session.flush()
            print(f"   - Created principal: Dr. Rajesh Kumar")
        else:
            print(f"   - Principal already exists")
            
        return principal
    
    def create_hods(self):
        """Create HOD for each department"""
        print("\n7. Creating HODs...")
        
        hod_names = {
            "Computer Science": "Dr. Srinivasan",
            "Computer Applications": "Dr. Lakshmi",
            "Commerce Finance": "Dr. Venkatesh",
            "Commerce Co-op": "Dr. Meena",
            "English": "Dr. Sharmila",
            "Economics": "Dr. Kumar",
            "History": "Dr. Rajan"
        }
        
        hods_created = 0
        
        for dept_name, hod_name in hod_names.items():
            dept = self.departments.get(dept_name)
            if not dept:
                continue
                
            username = f"hod_{dept.code.lower()}"
            
            hod = User.query.filter_by(username=username).first()
            
            if not hod:
                hod = User(
                    username=username,
                    email=f"{username}@college.edu",
                    full_name=hod_name,
                    role="hod",
                    department=dept_name,  # FIXED: Use department name string
                    password_hash=generate_password_hash(HOD_PASSWORD),
                    is_active=True
                )
                db.session.add(hod)
                hods_created += 1
                print(f"   - Created HOD: {hod_name} for {dept_name}")
            
        db.session.flush()
        print(f"   - Created {hods_created} new HODs")
        
    def create_coordinators(self):
        """Create coordinators (no department)"""
        print("\n8. Creating Coordinators...")
        
        coordinator = User.query.filter_by(username="coordinator").first()
        
        if not coordinator:
            coordinator = User(
                username="coordinator",
                email="coordinator@college.edu",
                full_name="Mr. Elamathi",
                role="coordinator",
                department=None,  # FIXED: Coordinator has no department
                password_hash=generate_password_hash(COORDINATOR_PASSWORD),
                is_active=True
            )
            db.session.add(coordinator)
            db.session.flush()
            print(f"   - Created coordinator: Mr. Elamathi (No Department)")
        else:
            print(f"   - Coordinator already exists")
            
        return coordinator
    
    def create_teachers(self):
        """Create 6 teachers per department"""
        print("\n9. Creating Teachers...")
        
        teachers_created = 0
        
        for dept_name, dept in self.departments.items():
            for i in range(1, 7):  # 6 teachers per department
                username = f"{dept.code.lower()}_teacher{i}"
                
                teacher = User.query.filter_by(username=username).first()
                
                if not teacher:
                    teacher = User(
                        username=username,
                        email=f"{username}@college.edu",
                        full_name=f"{dept_name} Teacher {i}",
                        role="teacher",
                        department=dept_name,  # FIXED: Use department name string
                        password_hash=generate_password_hash(TEACHER_PASSWORD),
                        is_active=True
                    )
                    db.session.add(teacher)
                    teachers_created += 1
                    print(f"   - Created teacher: {username} for {dept_name}")
                    
        db.session.flush()
        print(f"   - Created {teachers_created} new teachers")
        print(f"   - Total teachers: {User.query.filter_by(role='teacher').count()}")
    
    def get_next_student_sequence(self):
        """Get the next available sequence number for student IDs"""
        # Get all existing student IDs
        students = Student.query.all()
        max_sequence = 0
        
        for student in students:
            # Extract sequence number from student_id (assuming format like CS2025001)
            match = re.search(r'(\d+)$', student.student_id)
            if match:
                try:
                    sequence = int(match.group(1))
                    if sequence > max_sequence:
                        max_sequence = sequence
                except ValueError:
                    pass
        
        return max_sequence + 1
    
    def cleanup_malformed_students(self):
        """Clean up malformed student data and their related records"""
        print("\n   Checking for malformed student data...")
        
        # Find students with malformed IDs (like CS_2, CS_3, etc.)
        malformed_students = Student.query.filter(
            ~Student.student_id.like('CS2%') &  # Not starting with CS2 (year 2025)
            ~Student.student_id.like('CA2%') &  # Not starting with CA2
            ~Student.student_id.like('CF2%') &  # Not starting with CF2
            ~Student.student_id.like('CC2%') &  # Not starting with CC2
            ~Student.student_id.like('EN2%') &  # Not starting with EN2
            ~Student.student_id.like('EC2%') &  # Not starting with EC2
            ~Student.student_id.like('HY2%')    # Not starting with HY2
        ).all()
        
        if malformed_students:
            print(f"   Found {len(malformed_students)} malformed student records")
            for student in malformed_students:
                print(f"      - {student.student_id}: {student.name}")
            
            # Option to delete malformed students
            response = input("   Do you want to delete these malformed students? (y/n): ")
            if response.lower() == 'y':
                try:
                    # First, delete all related student_performance records
                    for student in malformed_students:
                        # Delete performance records
                        student_performances = StudentPerformance.query.filter_by(student_id=student.id).all()
                        for perf in student_performances:
                            db.session.delete(perf)
                        
                        # Delete attendance records if they exist
                        attendance_records = Attendance.query.filter_by(student_id=student.id).all()
                        for att in attendance_records:
                            db.session.delete(att)
                    
                    # Flush to ensure deletions are processed
                    db.session.flush()
                    
                    # Now delete the students and their users
                    for student in malformed_students:
                        # Delete the user associated with the student
                        if student.user_id:
                            user = User.query.get(student.user_id)
                            if user:
                                db.session.delete(user)
                        
                        # Delete the student
                        db.session.delete(student)
                    
                    db.session.flush()
                    print(f"   Successfully deleted {len(malformed_students)} malformed student records and their related data")
                    
                except Exception as e:
                    print(f"   Error during deletion: {e}")
                    db.session.rollback()
        else:
            print("   No malformed student records found")
    
    def generate_student_name(self, reg_number, dept_code, sequence):
        """
        Generate department-based student names.
        Each department gets its own set of names that repeat in a cycle.
        """
        # Department-specific name lists
        dept_names = {
            "CS": [  # Computer Science
                "Aarav", "Vihaan", "Vivaan", "Advik", "Kabir", "Arjun", "Rohan", "Ishaan",
                "Aryan", "Atharv", "Krishna", "Shaurya", "Yash", "Dhruv", "Rudra", "Samar",
                "Aayush", "Veer", "Ritvik", "Yuvaan", "Ranveer", "Vedant", "Pranav", "Karthik",
                "Nikhil", "Rahul", "Raj", "Amit", "Sunil", "Anil", "Sanjay", "Rajesh"
            ],
            "CA": [  # Computer Applications
                "Ananya", "Diya", "Aaradhya", "Sai", "Riya", "Anaya", "Aadhya", "Anvi",
                "Prisha", "Saanvi", "Pari", "Anika", "Navya", "Ishita", "Kavya", "Aarohi",
                "Siya", "Shanaya", "Tanvi", "Vanya", "Priya", "Neha", "Pooja", "Shruti",
                "Kavita", "Meena", "Rekha", "Lakshmi", "Radha", "Sita", "Gita", "Asha"
            ],
            "CF": [  # Commerce Finance
                "Arjun", "Rohan", "Krishna", "Shaurya", "Yash", "Dhruv", "Rudra", "Samar",
                "Karthik", "Nikhil", "Rahul", "Raj", "Amit", "Sunil", "Anil", "Sanjay",
                "Rajesh", "Rakesh", "Mukesh", "Suresh", "Ramesh", "Dinesh", "Mahesh", "Vijay",
                "Ajay", "Anand", "Praveen", "Manoj", "Vinod", "Prakash", "Hari", "Gopal"
            ],
            "CC": [  # Commerce Co-op
                "Meena", "Rekha", "Asha", "Usha", "Kala", "Mala", "Leela", "Shanta",
                "Radha", "Sita", "Gita", "Nita", "Geeta", "Neeta", "Reeta", "Seeta",
                "Lakshmi", "Saraswati", "Parvati", "Kavita", "Shobha", "Sangeeta", "Sunita", "Anita",
                "Manju", "Padmini", "Vimala", "Kamala", "Sharada", "Bhagyashree", "Vijayalakshmi", "Rukmini"
            ],
            "EN": [  # English
                "Arun", "Kiran", "Mohan", "Sohan", "Ravi", "Shyam", "Hari", "Gopal",
                "John", "David", "Michael", "Robert", "James", "William", "Richard", "Thomas",
                "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Susan", "Jessica", "Sarah",
                "George", "Paul", "Mark", "Steven", "Andrew", "Kenneth", "Joshua", "Kevin"
            ],
            "EC": [  # Economics
                "Ravi", "Anu", "Rajan", "Meera", "Gopal", "Krishna", "Mohan", "Sohan",
                "Arjun", "Karthik", "Nikhil", "Rahul", "Raj", "Amit", "Sunil", "Anil",
                "Priya", "Neha", "Pooja", "Shruti", "Kavita", "Meena", "Rekha", "Lakshmi",
                "Vijay", "Ajay", "Sanjay", "Rakesh", "Mukesh", "Suresh", "Ramesh", "Dinesh"
            ],
            "HY": [  # History
                "Arun", "Kavita", "Mohan", "Shruti", "Prakash", "Deepa", "Rajesh", "Sunita",
                "Raj", "Rani", "Raja", "Rani", "Veer", "Veera", "Singh", "Kaur",
                "Ashok", "Ashoka", "Chandragupta", "Vikramaditya", "Akbar", "Shahjahan", "Shivaji", "Ranjit",
                "Lakshmibai", "Jhansi", "Tipu", "Sultan", "Krishnadevaraya", "Harsha", "Maurya", "Gupta"
            ]
        }
        
        # Get the name list for this department, or use a default if not found
        name_list = dept_names.get(dept_code, ["Student"])
        
        # Cycle through names based on sequence number
        # This ensures the same student gets the same name across runs
        name_index = (sequence - 1) % len(name_list)
        first_name = name_list[name_index]
        
        # Add a surname based on department
        surnames = {
            "CS": ["Sharma", "Verma", "Patel", "Singh", "Kumar", "Reddy", "Gupta", "Joshi"],
            "CA": ["Mishra", "Yadav", "Jha", "Pandey", "Tiwari", "Dubey", "Tripathi", "Chauhan"],
            "CF": ["Rao", "Naidu", "Menon", "Nair", "Pillai", "Kurian", "Mathew", "Thomas"],
            "CC": ["Desai", "Shah", "Mehta", "Trivedi", "Acharya", "Bhatt", "Dave", "Sen"],
            "EN": ["Fernandez", "D'Souza", "Pereira", "Gonsalves", "Rodrigues", "D'Costa", "Almeida", "Fernandes"],
            "EC": ["Khan", "Ansari", "Sheikh", "Begum", "Ali", "Ahmed", "Hussain", "Iqbal"],
            "HY": ["Nayak", "Sahoo", "Mahapatra", "Swain", "Behera", "Parida", "Rout", "Pradhan"]
        }
        
        surname_list = surnames.get(dept_code, ["Student"])
        surname_index = ((sequence - 1) // len(name_list)) % len(surname_list)
        last_name = surname_list[surname_index]
        
        return f"{first_name} {last_name}"
        
    def create_all_students(self):
        """Create 120 students per department (15 per semester) with dynamic names"""
        print("\n10. Creating Students...")
        
        students_created = 0
        students_skipped = 0
        all_semesters = [1, 2, 3, 4, 5, 6, 7, 8]
        
        # First, clean up any malformed student data if needed
        self.cleanup_malformed_students()
        
        # Get the count of existing students
        existing_count = Student.query.count()
        print(f"   Existing students in database: {existing_count}")
        
        # Calculate how many students we need to create
        expected_total = len(self.departments) * TOTAL_STUDENTS_PER_DEPT
        needed_students = expected_total - existing_count
        
        if needed_students <= 0:
            print(f"   Database already has {existing_count} students, which meets or exceeds expected {expected_total}")
            print(f"   Skipping student creation - existing data preserved")
            return
        
        print(f"   Need to create {needed_students} new students")
        
        # Get the next available sequence number
        next_sequence = self.get_next_student_sequence()
        print(f"   Starting student sequence from: {next_sequence}")
        
        # Track global sequence across ALL students
        global_sequence = next_sequence - 1  # Subtract 1 because we'll increment before use
        
        for dept_name, dept in self.departments.items():
            course = self.courses.get(dept_name)
            if not course:
                continue
                
            print(f"\n   Processing students for {dept_name}...")
            
            # Count existing students in this department
            existing_dept_students = Student.query.filter_by(department_id=dept.id).count()
            dept_needed = TOTAL_STUDENTS_PER_DEPT - existing_dept_students
            
            if dept_needed <= 0:
                print(f"      Department already has {existing_dept_students} students, skipping")
                continue
                
            print(f"      Need {dept_needed} more students for {dept_name}")
            
            # Create students until we reach the required number for this department
            students_created_in_dept = 0
            
            # Loop through semesters to create missing students
            for sem_num in all_semesters:
                if students_created_in_dept >= dept_needed:
                    break
                    
                # Count existing students in this semester for this department
                existing_semester_students = Student.query.filter_by(
                    department_id=dept.id,
                    current_semester=sem_num
                ).count()
                
                semester_needed = STUDENTS_PER_SEMESTER - existing_semester_students
                
                if semester_needed <= 0:
                    print(f"         Semester {sem_num} already has {existing_semester_students} students")
                    continue
                    
                print(f"         Semester {sem_num}: need {semester_needed} students")
                
                # Calculate approximate batch year
                year = (sem_num + 1) // 2
                batch_year = get_batch_from_year(year)
                
                # Create missing students for this semester
                for i in range(semester_needed):
                    # Increment global sequence for EACH student
                    global_sequence += 1
                    
                    # Generate registration number and student ID
                    reg_number = generate_registration_number(dept_name, batch_year, global_sequence)
                    student_id = generate_student_id(dept_name, batch_year, global_sequence)
                    
                    # Generate default name based on department
                    default_name = self.generate_student_name(reg_number, dept.code, global_sequence)
                    username = f"{dept.code.lower()}_{default_name.lower().replace(' ', '_')}_{global_sequence}"
                    
                    # Check if student already exists by registration number or student_id
                    existing_student = Student.query.filter(
                        (Student.registration_number == reg_number) | 
                        (Student.student_id == student_id)
                    ).first()
                    
                    if existing_student:
                        print(f"         Student {reg_number} already exists with name: {existing_student.name}")
                        print(f"         Keeping existing name - will not overwrite")
                        students_skipped += 1
                        continue
                    
                    # Check if user exists
                    user = User.query.filter_by(username=username).first()
                    
                    if not user:
                        try:
                            # Create user - FIXED: Use department name string
                            user = User(
                                username=username,
                                email=f"{username}@college.edu",
                                full_name=default_name,
                                role="student",
                                department=dept_name,  # FIXED: Use department name string
                                password_hash=generate_password_hash(STUDENT_PASSWORD),
                                is_active=True
                            )
                            db.session.add(user)
                            db.session.flush()
                            
                            # Create student record - this uses department_id (correct)
                            student = Student(
                                registration_number=reg_number,
                                student_id=student_id,
                                name=default_name,
                                email=f"{username}@college.edu",
                                phone=f"987654{global_sequence:04d}",
                                user_id=user.id,
                                course_id=course.id,
                                department_id=dept.id,  # This is correct - Student uses department_id
                                current_semester=sem_num,
                                batch_year=batch_year,
                                admission_date=date(batch_year, 6, 15),
                                is_active=True
                            )
                            db.session.add(student)
                            students_created += 1
                            students_created_in_dept += 1
                            
                            if students_created % 20 == 0:
                                print(f"         Created {students_created} students so far...")
                                db.session.flush()
                                
                        except Exception as e:
                            print(f"         Error creating student: {e}")
                            db.session.rollback()
                            # Continue with next sequence
                            continue
                    else:
                        print(f"         User {username} already exists, skipping")
                        students_skipped += 1
            
            print(f"   Completed {students_created_in_dept} new students for {dept_name}")
        
        db.session.flush()
        print(f"\n   - Created {students_created} new students")
        print(f"   - Skipped {students_skipped} existing students (names preserved)")
        
        total_students = Student.query.count()
        print(f"   - Total students in database: {total_students} / {expected_total}")
        
        # Show sample of students
        print(f"\n   Sample students:")
        sample_students = Student.query.order_by(Student.id.desc()).limit(5).all()
        for s in sample_students:
            print(f"      • {s.name} (Sem {s.current_semester}) - {s.student_id}")
        
    def verify_setup(self):
        """Verify the academic setup"""
        print("\n" + "-" * 40)
        print("SETUP VERIFICATION")
        print("-" * 40)
        
        print("\nDatabase Counts:")
        print(f"   Academic Years: {AcademicYear.query.count()}")
        print(f"   Departments: {Department.query.count()}")
        print(f"   Courses: {Course.query.count()}")
        print(f"   Semesters: {Semester.query.count()}")
        print(f"   Subjects: {Subject.query.count()}")
        print(f"   Users: {User.query.count()}")
        print(f"   Students: {Student.query.count()}")
        
        print("\nUsers by Role:")
        roles = ['principal', 'hod', 'coordinator', 'teacher', 'student']
        for role in roles:
            count = User.query.filter_by(role=role).count()
            print(f"   {role.capitalize()}: {count}")
            
        print("\nStudents per Department:")
        for dept_name, dept in self.departments.items():
            count = Student.query.filter_by(department_id=dept.id).count()
            expected = TOTAL_STUDENTS_PER_DEPT
            print(f"   {dept_name}: {count} / {expected} students")

# =====================================================
# MAIN EXECUTION
# =====================================================

def run_auto_setup():
    """Main function to run auto setup"""
    from app import create_app
    from extensions import db
    
    # Create app
    app = create_app('development')
    
    # IMPORTANT: Create all database tables first!
    with app.app_context():
        print("\n" + "=" * 60)
        print("CREATING DATABASE TABLES")
        print("=" * 60)
        db.create_all()
        print(" Database tables created successfully!")
    
    # Run setup with app context
    setup = AcademicAutoSetup(app)
    setup.setup_all()
    
    print("\n" + "=" * 60)
    print("ACADEMIC SUMMARY")
    print("=" * 60)
    print(f"""
Academic Year: 2025-2026
Semester Type: {'Odd' if setup.current_semester_type == 1 else 'Even'}
Departments: 7
Courses: 7
Semesters: 8 per course x 7 departments = 56
Subjects: ~40 per department x 7 = ~280
Teachers: 6 per department x 7 = 42
Students: 120 per department x 7 = 840
    """)
    print("=" * 60)

if __name__ == "__main__":
    run_auto_setup()