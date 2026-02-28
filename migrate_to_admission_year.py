# migrate_to_admission_year.py
"""
Run this script to migrate from batch_year to admission_year
and set up proper semester calculation
"""

from app import create_app
from model import Student, db
from datetime import datetime

app = create_app('development')

with app.app_context():
    print("=" * 60)
    print("MIGRATING TO ADMISSION YEAR SYSTEM")
    print("=" * 60)
    
    # First, check if admission_year column exists
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    columns = [c['name'] for c in inspector.get_columns('students')]
    
    if 'admission_year' not in columns:
        print("  admission_year column not found!")
        print("\nYou need to add admission_year to Student model first.")
        print("\nAdd this to your Student model in model.py:")
        print("""
    # REPLACE THIS:
    batch_year = db.Column(db.Integer, nullable=False)
    
    # WITH THESE:
    admission_year = db.Column(db.Integer, nullable=False)  # e.g., 2022, 2023, 2024, 2025
    # Keep batch_year temporarily if needed, or remove it
        """)
        exit()
    
    # Get all students
    students = Student.query.all()
    print(f"Found {len(students)} students")
    
    migrated_count = 0
    skipped_count = 0
    
    for student in students:
        # Check if admission_year is already set
        if student.admission_year:
            print(f"✓ {student.name}: admission_year already = {student.admission_year}")
            skipped_count += 1
            continue
        
        # If you have batch_year field, migrate to admission_year
        if hasattr(student, 'batch_year') and student.batch_year:
            # Map batch_year to admission_year
            student.admission_year = student.batch_year
            print(f"→ {student.name}: batch_year={student.batch_year} → admission_year={student.admission_year}")
            migrated_count += 1
        else:
            # If no batch_year, try to extract from registration number
            try:
                # Example: CA2025121 → year = 2025
                reg_year = int(str(student.registration_number)[2:6])
                student.admission_year = reg_year
                print(f"→ {student.name}: extracted from reg_no={student.registration_number} → admission_year={reg_year}")
                migrated_count += 1
            except:
                # Default to current year - 4 (assuming 4th year)
                default_year = datetime.now().year - 4
                student.admission_year = default_year
                print(f"⚠️  {student.name}: No data found, set default={default_year}")
                migrated_count += 1
    
    # Commit changes
    db.session.commit()
    
    print("\n" + "=" * 60)
    print("MIGRATION SUMMARY")
    print("=" * 60)
    print(f"Migrated: {migrated_count} students")
    print(f"  Skipped: {skipped_count} students")
    print(f" Total: {migrated_count + skipped_count} students")
    
    # Show sample
    print("\n" + "=" * 60)
    print("SAMPLE STUDENTS AFTER MIGRATION")
    print("=" * 60)
    sample = Student.query.limit(5).all()
    for s in sample:
        print(f"• {s.name}: admission_year={s.admission_year}, current_semester={s.current_semester}")
    
    print("\n" + "=" * 60)
    print(" MIGRATION COMPLETE!")
    print("=" * 60)
    print("\nNow your system will automatically calculate semesters based on admission_year!")