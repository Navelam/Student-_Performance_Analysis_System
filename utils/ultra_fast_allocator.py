# utils/ultra_fast_allocator.py
"""
Ultra Fast Teacher-Subject Allocator - Even Semesters Only
Assigns subjects for current semesters (2,4,6,8)
"""

from model import User, Subject, TeacherSubject, AcademicYear
from extensions import db
from collections import defaultdict

class UltraFastAllocator:
    """Ultra Fast AI Allocator - Even Semesters Only"""
    
    def __init__(self, department_id, academic_year="2025-2026"):
        self.department_id = department_id
        self.academic_year = academic_year
        self.max_subjects = 5
        self.current_semesters = [2, 4, 6, 8]
        
    def assign_now(self):
        """Instant assignment for even semesters only"""
        try:
            # Get academic year
            ac_year = AcademicYear.query.filter_by(year=self.academic_year).first()
            if not ac_year:
                return {'success': False, 'message': 'Academic year not found'}
            
            # Get teachers
            teachers = User.query.filter_by(
                role='teacher', 
                department_id=self.department_id,
                is_active=True
            ).all()
            
            # Get ONLY subjects for even semesters
            subjects = Subject.query.filter(
                Subject.department_id == self.department_id,
                Subject.semester_id.in_(self.current_semesters)
            ).all()
            
            subjects_by_semester = defaultdict(list)
            for subject in subjects:
                subjects_by_semester[subject.semester_id].append(subject)
            
            if not teachers or not subjects:
                return {
                    'success': False, 
                    'message': f'No teachers or subjects for even semesters {self.current_semesters}'
                }
            
            # Get existing assignments for even semesters
            even_subject_ids = [s.id for s in subjects]
            existing_assignments = TeacherSubject.query.filter(
                TeacherSubject.academic_year_id == ac_year.id,
                TeacherSubject.is_active == True,
                TeacherSubject.subject_id.in_(even_subject_ids)
            ).all()
            
            existing_subject_ids = {a.subject_id for a in existing_assignments}
            teacher_counts = defaultdict(int)
            
            for a in existing_assignments:
                teacher_counts[a.teacher_id] += 1
            
            # Create new assignments
            new_assignments = []
            teacher_list = list(teachers)
            
            print(f"\n⚡ Ultra Fast Assign - Even Semesters Only")
            print(f"   Semesters: {self.current_semesters}")
            print(f"   Teachers: {len(teachers)}")
            print(f"   Subjects: {len(subjects)}")
            print(f"   Already assigned: {len(existing_assignments)}")
            
            # Process each even semester
            for semester_id in self.current_semesters:
                semester_subjects = subjects_by_semester.get(semester_id, [])
                unassigned = [s for s in semester_subjects if s.id not in existing_subject_ids]
                
                if not unassigned:
                    continue
                
                # Find available teachers
                available_teachers = [
                    t for t in teacher_list 
                    if teacher_counts[t.id] < self.max_subjects
                ]
                
                if not available_teachers:
                    print(f"   Semester {semester_id}: No available teachers")
                    continue
                
                # Distribute subjects
                for i, subject in enumerate(unassigned):
                    if not available_teachers:
                        break
                    
                    # Round-robin
                    teacher = available_teachers[i % len(available_teachers)]
                    
                    new_assignments.append({
                        'teacher_id': teacher.id,
                        'subject_id': subject.id,
                        'academic_year_id': ac_year.id,
                        'semester_id': subject.semester_id,
                        'is_active': True
                    })
                    
                    teacher_counts[teacher.id] += 1
                    
                    if teacher_counts[teacher.id] >= self.max_subjects:
                        available_teachers = [t for t in available_teachers if t.id != teacher.id]
                
                print(f"   Semester {semester_id}: Assigned {len([a for a in new_assignments if a['semester_id'] == semester_id])} subjects")
            
            # Bulk insert
            if new_assignments:
                db.session.bulk_insert_mappings(TeacherSubject, new_assignments)
                db.session.commit()
                print(f"\n✅ Created {len(new_assignments)} new assignments")
            else:
                print(f"\n✅ No new assignments needed")
            
            return {
                'success': True,
                'assigned': len(new_assignments),
                'total': len(subjects),
                'existing': len(existing_assignments),
                'semesters': self.current_semesters
            }
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {str(e)}")
            return {'success': False, 'message': str(e)}