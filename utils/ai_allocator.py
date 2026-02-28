# utils/ai_allocator.py
"""
AI-based Teacher-Subject Allocator - Even Semesters Only (2,4,6,8)
With proper semester mapping
"""

from model import User, Subject, TeacherSubject, AcademicYear, Department
from extensions import db
import random
from collections import defaultdict
from utils.helpers import DEPARTMENTS

class TeacherSubjectAllocator:  # Make sure this class name matches the import
    """AI Allocator for assigning teachers to subjects - Even Semesters Only"""
    
    def __init__(self, department_id, academic_year="2025-2026"):
        self.department_id = department_id
        self.academic_year_str = academic_year
        self.academic_year_obj = None
        self.teachers = []
        self.subjects = []
        self.teacher_workload = {}
        self.subjects_by_semester = defaultdict(list)
        self.max_subjects_per_teacher = 5
        self.even_semesters = [2, 4, 6, 8]  # Even semesters
        
    def load_data_fast(self):
        """Load data quickly with minimal queries"""
        # Get academic year object
        self.academic_year_obj = AcademicYear.query.filter_by(
            year=self.academic_year_str
        ).first()
        
        if not self.academic_year_obj:
            from datetime import date
            start_year = int(self.academic_year_str.split('-')[0])
            end_year = int(self.academic_year_str.split('-')[1])
            self.academic_year_obj = AcademicYear(
                year=self.academic_year_str,
                start_date=date(start_year, 6, 1),
                end_date=date(end_year, 4, 30),
                is_current=True
            )
            db.session.add(self.academic_year_obj)
            db.session.flush()
        
        # Get department
        department = Department.query.get(self.department_id)
        if not department:
            print(f"Department with ID {self.department_id} not found")
            return False
            
        dept_name = department.name
        dept_code = department.code
        
        # Get teachers
        self.teachers = User.query.filter(
            User.role == 'teacher',
            db.or_(
                User.department == dept_name,
                User.department == dept_code
            ),
            User.is_active == True
        ).all()
        
        # Get subjects for this department
        self.subjects = Subject.query.filter_by(
            department_id=self.department_id
        ).all()
        
        # Group subjects by semester
        for subject in self.subjects:
            self.subjects_by_semester[subject.semester_id].append(subject)
        
        # Get existing assignments
        all_assignments = TeacherSubject.query.filter(
            TeacherSubject.academic_year_id == self.academic_year_obj.id,
            TeacherSubject.is_active == True
        ).all()
        
        self.assigned_subjects = {a.subject_id for a in all_assignments}
        
        # Calculate teacher workload
        self.teacher_workload = {}
        for assignment in all_assignments:
            teacher_id = assignment.teacher_id
            self.teacher_workload[teacher_id] = self.teacher_workload.get(teacher_id, 0) + 1
        
        return True
    
    def assign_teachers_fast(self):
        """Fast AI assignment algorithm"""
        if not self.load_data_fast():
            return {
                'success': False,
                'message': 'Failed to load data',
                'assignments': []
            }
        
        if not self.teachers:
            return {
                'success': False,
                'message': 'No teachers found in department',
                'assignments': []
            }
        
        assignments = []
        
        # Track assignments per teacher
        teacher_assignment_count = {teacher.id: self.teacher_workload.get(teacher.id, 0) 
                                   for teacher in self.teachers}
        
        # Process each even semester
        for semester_id in self.even_semesters:
            subjects = self.subjects_by_semester.get(semester_id, [])
            unassigned = [s for s in subjects if s.id not in self.assigned_subjects]
            
            if not unassigned:
                continue
            
            # Create teacher pool
            available_teachers = []
            for teacher in self.teachers:
                current_load = teacher_assignment_count.get(teacher.id, 0)
                if current_load < self.max_subjects_per_teacher:
                    slots_left = self.max_subjects_per_teacher - current_load
                    available_teachers.extend([teacher] * slots_left)
            
            random.shuffle(available_teachers)
            
            # Assign subjects
            for subject in unassigned:
                if not available_teachers:
                    break
                
                teacher = available_teachers.pop(0)
                
                assignment = TeacherSubject(
                    teacher_id=teacher.id,
                    subject_id=subject.id,
                    academic_year_id=self.academic_year_obj.id,
                    semester_id=subject.semester_id,
                    is_active=True
                )
                assignments.append(assignment)
                
                teacher_assignment_count[teacher.id] += 1
                self.assigned_subjects.add(subject.id)
        
        return {
            'success': True,
            'assignments': assignments,
            'total_assigned': len(assignments)
        }
    
    def reset_assignments_fast(self):
        """Reset all active assignments"""
        self.load_data_fast()
        
        subject_ids = [s.id for s in self.subjects]
        
        result = TeacherSubject.query.filter(
            TeacherSubject.academic_year_id == self.academic_year_obj.id,
            TeacherSubject.is_active == True,
            TeacherSubject.subject_id.in_(subject_ids)
        ).update({'is_active': False}, synchronize_session=False)
        
        db.session.commit()
        return result
    
    def get_assignment_stats_fast(self):
        """Get assignment statistics"""
        self.load_data_fast()
        
        stats = {
            'total_teachers': len(self.teachers),
            'total_subjects': len(self.subjects),
            'assigned_subjects': len(self.assigned_subjects),
            'teacher_workload': {},
            'average_workload': 0,
            'max_capacity': self.max_subjects_per_teacher
        }
        
        total = 0
        for teacher in self.teachers:
            workload = self.teacher_workload.get(teacher.id, 0)
            stats['teacher_workload'][teacher.full_name] = workload
            total += workload
        
        if self.teachers:
            stats['average_workload'] = round(total / len(self.teachers), 2)
        
        return stats