# init_db.py
from app import create_app
from extensions import db
from model import User, Department, Course, AcademicYear, Semester, Subject, Student, TeacherSubject, StudentPerformance, Attendance, Notification, UserNotification, ExamTimetable, ExamRoomAllocation, SeatingArrangement, InvigilatorAssignment
from datetime import datetime, date

app = create_app('development')

with app.app_context():
    print("Creating database tables...")
    db.create_all()
    print("✅ Database tables created successfully!")
    
    # Check if we need to create initial data
    if Department.query.count() == 0:
        print("\nCreating initial departments...")
        departments = [
            {"name": "Computer Science", "code": "CS"},
            {"name": "Computer Applications", "code": "CA"},
            {"name": "Commerce Finance", "code": "CF"},
            {"name": "Commerce Co-op", "code": "CC"},
            {"name": "English", "code": "EN"},
            {"name": "Economics", "code": "EC"},
            {"name": "History", "code": "HY"}
        ]
        
        for dept_data in departments:
            dept = Department(name=dept_data["name"], code=dept_data["code"])
            db.session.add(dept)
        
        db.session.commit()
        print(f"✅ Created {len(departments)} departments")
    
    # Create academic year
    if AcademicYear.query.count() == 0:
        print("\nCreating academic year...")
        current_year = datetime.now().year
        if datetime.now().month >= 6:
            year_str = f"{current_year}-{current_year+1}"
            start_date = date(current_year, 6, 1)
            end_date = date(current_year+1, 4, 30)
        else:
            year_str = f"{current_year-1}-{current_year}"
            start_date = date(current_year-1, 6, 1)
            end_date = date(current_year, 4, 30)
        
        ac_year = AcademicYear(
            year=year_str,
            start_date=start_date,
            end_date=end_date,
            is_current=True
        )
        db.session.add(ac_year)
        db.session.commit()
        print(f"✅ Created academic year: {year_str}")
    
    # Create courses for departments
    if Course.query.count() == 0:
        print("\nCreating courses...")
        departments = Department.query.all()
        for dept in departments:
            course = Course(
                name=f"{dept.name} Program",
                code=f"{dept.code}_PROG",
                duration_years=3,
                department_id=dept.id
            )
            db.session.add(course)
        
        db.session.commit()
        print(f"✅ Created courses for {len(departments)} departments")
    
    # Create a default admin/coordinator user
    if User.query.filter_by(username='admin').count() == 0:
        print("\nCreating default admin user...")
        admin = User(
            username='admin',
            email='admin@college.edu',
            full_name='System Administrator',
            role='coordinator',
            department=None,
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✅ Created admin user: username='admin', password='admin123'")
    
    print("\n" + "="*50)
    print("DATABASE INITIALIZATION COMPLETE!")
    print("="*50)
    print(f"\nTables created: {len(db.metadata.tables)}")
    print(f"Departments: {Department.query.count()}")
    print(f"Courses: {Course.query.count()}")
    print(f"Academic Years: {AcademicYear.query.count()}")
    print(f"Users: {User.query.count()}")