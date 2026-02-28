"""
ROOM ALLOCATION FOR ALL EXAM DATES
Run this script to allocate rooms for every date that has exams
Each date gets its own rooms based on number of exams
"""

from app import create_app
from model import ExamRoomAllocation, SeatingArrangement, Student, ExamTimetable, Department
from datetime import date
import random
from extensions import db

app = create_app('development')

with app.app_context():
    print("=" * 70)
    print("ROOM ALLOCATION FOR ALL EXAM DATES")
    print("=" * 70)
    
    # Get all unique exam dates from database
    exam_dates = db.session.query(ExamTimetable.exam_date).distinct().order_by(ExamTimetable.exam_date).all()
    
    if not exam_dates:
        print("No exam dates found in database")
        print("Please create exam timetable first")
        exit()
    
    print(f"\nFound {len(exam_dates)} dates with exams:")
    for d in exam_dates:
        exam_count = ExamTimetable.query.filter_by(exam_date=d[0]).count()
        print(f"  {d[0]}: {exam_count} exams")
    
    # Get all students
    all_students = Student.query.all()
    total_students = len(all_students)
    
    if total_students == 0:
        print("No students found in database")
        exit()
    
    print(f"\nTotal students available: {total_students}")
    
    # Track overall statistics
    total_dates_processed = 0
    total_rooms_created = 0
    total_students_allocated = 0
    
    # Process EACH date separately
    for date_row in exam_dates:
        current_date = date_row[0]
        
        print(f"\n{'-' * 50}")
        print(f"Processing {current_date}...")
        
        # Count exams for this date
        exam_count = ExamTimetable.query.filter_by(exam_date=current_date).count()
        
        # Calculate students needed for this date
        # Using formula: students = exam_count * 6 (adjust based on your needs)
        students_needed = exam_count * 15
        
        if students_needed > total_students:
            students_needed = total_students
        
        print(f"  Exams: {exam_count}, Students needed: {students_needed}")
        
        if students_needed == 0:
            print("  No students needed - skipping")
            continue
        
        # Check if rooms already exist for this date
        existing_rooms = ExamRoomAllocation.query.filter_by(exam_date=current_date).count()
        if existing_rooms > 0:
            print(f"  Found {existing_rooms} existing rooms for {current_date}")
            print(f"  Deleting existing allocations for {current_date}")
            # Delete existing allocations for this date only
            SeatingArrangement.query.filter_by(exam_date=current_date).delete()
            ExamRoomAllocation.query.filter_by(exam_date=current_date).delete()
            db.session.commit()
            print(f"  Deleted {existing_rooms} old rooms")
        
        # Get students and shuffle
        random.shuffle(all_students)
        students_to_use = all_students[:students_needed]
        
        # Group students by department for mixing
        students_by_dept = {}
        
        # Initialize department groups
        for dept in Department.query.all():
            students_by_dept[dept.name] = []
        
        # Add students to their department groups
        for student in students_to_use:
            students_by_dept[student.department.name].append(student)
        
        # Shuffle each department's students
        for dept in students_by_dept:
            random.shuffle(students_by_dept[dept])
        
        # Create interleaved list (mix departments)
        ordered_students = []
        dept_names = list(students_by_dept.keys())
        
        while any(students_by_dept[d] for d in dept_names):
            for dept in dept_names:
                if students_by_dept[dept]:
                    ordered_students.append(students_by_dept[dept].pop(0))
        
        # Calculate rooms needed
        room_capacity = 20
        rooms_needed = (len(ordered_students) + room_capacity - 1) // room_capacity
        
        # Maximum rooms available (6 blocks * 15 rooms = 90)
        if rooms_needed > 90:
            rooms_needed = 90
            ordered_students = ordered_students[:rooms_needed * room_capacity]
        
        print(f"  Creating {rooms_needed} rooms...")
        
        # Room allocation
        blocks = ['A', 'B', 'C', 'D', 'E', 'F']
        student_index = 0
        rooms_created = []
        
        for block in blocks:
            if student_index >= len(ordered_students):
                break
                
            for room_num in range(101, 116):  # 101 to 115
                if student_index >= len(ordered_students):
                    break
                    
                room_number = f"{block}{room_num}"
                students_in_room = []
                
                # Fill this room
                for seat in range(1, room_capacity + 1):
                    if student_index < len(ordered_students):
                        student = ordered_students[student_index]
                        students_in_room.append({
                            'student': student,
                            'seat': seat
                        })
                        student_index += 1
                
                if not students_in_room:
                    continue
                
                # Use 10AM for all rooms (you can modify to split between 10AM/2PM)
                exam_time = '10AM'
                
                # Create room allocation record
                room = ExamRoomAllocation(
                    exam_date=current_date,
                    exam_time=exam_time,
                    block=block,
                    room_number=room_number,
                    capacity=room_capacity,
                    total_students=len(students_in_room),
                    created_by=1  # Assuming coordinator ID 1
                )
                db.session.add(room)
                db.session.flush()  # Get the ID
                
                # Create seating arrangements
                for item in students_in_room:
                    seating = SeatingArrangement(
                        room_allocation_id=room.id,
                        exam_date=current_date,
                        exam_time=exam_time,
                        block=block,
                        room_number=room_number,
                        seat_number=item['seat'],
                        student_id=item['student'].id,
                        reg_number=item['student'].registration_number,
                        student_name=item['student'].name,
                        department=item['student'].department.name
                    )
                    db.session.add(seating)
                
                rooms_created.append({
                    'room': room_number,
                    'students': len(students_in_room),
                    'block': block
                })
                
                # Commit in batches
                if student_index % 100 == 0 and student_index > 0:
                    db.session.commit()
        
        # Final commit for this date
        db.session.commit()
        
        # Calculate statistics for this date
        total_students_allocated_date = sum(r['students'] for r in rooms_created)
        full_rooms = sum(1 for r in rooms_created if r['students'] == 20)
        partial_rooms = sum(1 for r in rooms_created if r['students'] < 20)
        
        print(f"  Allocated {total_students_allocated_date} students in {len(rooms_created)} rooms")
        print(f"    Full rooms: {full_rooms}, Partial rooms: {partial_rooms}")
        print(f"    View at: http://localhost:5000/coordinator/view-room-allocation/{current_date}")
        
        # Update totals
        total_dates_processed += 1
        total_rooms_created += len(rooms_created)
        total_students_allocated += total_students_allocated_date
    
    # Summary of all dates
    print(f"\n{'=' * 70}")
    print("ALLOCATION COMPLETE FOR ALL DATES")
    print("=" * 70)
    print(f"\nOverall Summary:")
    print(f"  Dates processed: {total_dates_processed}")
    print(f"  Total rooms created: {total_rooms_created}")
    print(f"  Total students allocated: {total_students_allocated}")
    
    # Show final counts per date
    final_counts = db.session.query(
        ExamRoomAllocation.exam_date,
        db.func.count(ExamRoomAllocation.id).label('room_count'),
        db.func.sum(ExamRoomAllocation.total_students).label('student_count')
    ).group_by(ExamRoomAllocation.exam_date).order_by(ExamRoomAllocation.exam_date).all()
    
    print("\nFinal Allocation Summary by Date:")
    for fc in final_counts:
        print(f"  {fc.exam_date}: {fc.room_count} rooms, {fc.student_count} students")