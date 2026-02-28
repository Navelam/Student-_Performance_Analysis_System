# routes/principal_routes.py
from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify, make_response
from flask_login import login_required, current_user
from functools import wraps
from extensions import db
from model import (
    User, Student, TeacherSubject, Subject, Department, 
    StudentPerformance, AcademicYear, Semester, Attendance,
    ExamTimetable, Course
)
from datetime import datetime, date
import csv
from io import StringIO
import json

principal_bp = Blueprint('principal', __name__, url_prefix='/principal')

# =====================================================
# DECORATOR - Principal access only
# =====================================================

def principal_required(f):
    """Decorator to restrict access to principal only"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'principal':
            flash('Access denied. Principal privileges required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# =====================================================
# CONTEXT PROCESSOR
# =====================================================

@principal_bp.context_processor
def utility_processor():
    """Add utility functions to template context"""
    return {
        'now': datetime.now(),
        'today': date.today()
    }

# =====================================================
# DASHBOARD
# =====================================================

@principal_bp.route('/dashboard')
@login_required
@principal_required
def dashboard():
    """Principal Dashboard with summary statistics"""
    
    # Basic counts
    total_students = Student.query.count()
    total_teachers = User.query.filter_by(role='teacher', is_active=True).count()
    total_departments = Department.query.count()
    total_subjects = Subject.query.count()
    
    # Risk statistics
    critical_risk_count = StudentPerformance.query.filter(
        StudentPerformance.risk_status.in_(['Critical', 'High Risk'])
    ).count()
    
    # Attendance statistics
    attendance_records = Attendance.query.all()
    if attendance_records:
        overall_attendance = sum(a.attendance_percentage for a in attendance_records) / len(attendance_records)
    else:
        overall_attendance = 0
    
    # Department statistics
    dept_stats = []
    departments = Department.query.all()
    for dept in departments:
        dept_students = Student.query.filter_by(department_id=dept.id).count()
        dept_teachers = User.query.filter_by(role='teacher', department=dept.code).count()
        dept_stats.append({
            'name': dept.name,
            'students': dept_students,
            'teachers': dept_teachers
        })
    
    # Performance summary
    performances = StudentPerformance.query.all()
    avg_marks = 0
    if performances:
        avg_marks = sum(p.final_internal for p in performances) / len(performances)
    
    # Risk distribution
    risk_counts = {
        'Critical': StudentPerformance.query.filter_by(risk_status='Critical').count(),
        'High Risk': StudentPerformance.query.filter_by(risk_status='High Risk').count(),
        'Average': StudentPerformance.query.filter_by(risk_status='Average').count(),
        'Safe': StudentPerformance.query.filter_by(risk_status='Safe').count(),
        'Best': StudentPerformance.query.filter_by(risk_status='Best').count()
    }
    
    return render_template('principal/dashboard.html',
                         total_students=total_students,
                         total_teachers=total_teachers,
                         total_departments=total_departments,
                         total_subjects=total_subjects,
                         critical_risk_count=critical_risk_count,
                         overall_attendance=round(overall_attendance, 1),
                         dept_stats=dept_stats,
                         avg_marks=round(avg_marks, 1),
                         risk_counts=risk_counts,
                         now=datetime.now())


# =====================================================
# PERFORMANCE ANALYTICS
# =====================================================

@principal_bp.route('/analytics')
@login_required
@principal_required
def analytics():
    """Performance analytics with charts"""
    
    # Department-wise performance
    departments = Department.query.all()
    dept_performance = []
    
    for dept in departments:
        students = Student.query.filter_by(department_id=dept.id).all()
        student_ids = [s.id for s in students]
        
        performances = StudentPerformance.query.filter(
            StudentPerformance.student_id.in_(student_ids)
        ).all()
        
        if performances:
            avg_marks = sum(p.final_internal for p in performances) / len(performances)
            avg_attendance = sum(p.attendance for p in performances) / len(performances)
        else:
            avg_marks = 0
            avg_attendance = 0
        
        dept_performance.append({
            'name': dept.name,
            'avg_marks': round(avg_marks, 1),
            'avg_attendance': round(avg_attendance, 1),
            'student_count': len(students)
        })
    
    # Semester-wise performance
    semester_performance = []
    for sem in range(1, 9):
        performances = StudentPerformance.query.filter_by(semester=sem).all()
        if performances:
            avg_marks = sum(p.final_internal for p in performances) / len(performances)
            avg_attendance = sum(p.attendance for p in performances) / len(performances)
            student_count = len(set(p.student_id for p in performances))
        else:
            avg_marks = 0
            avg_attendance = 0
            student_count = 0
        
        semester_performance.append({
            'semester': sem,
            'avg_marks': round(avg_marks, 1),
            'avg_attendance': round(avg_attendance, 1),
            'student_count': student_count
        })
    
    # Risk distribution
    risk_counts = {
        'Critical': StudentPerformance.query.filter_by(risk_status='Critical').count(),
        'High Risk': StudentPerformance.query.filter_by(risk_status='High Risk').count(),
        'Average': StudentPerformance.query.filter_by(risk_status='Average').count(),
        'Safe': StudentPerformance.query.filter_by(risk_status='Safe').count(),
        'Best': StudentPerformance.query.filter_by(risk_status='Best').count()
    }
    
    # Subject-wise performance
    subject_performance = []
    subjects = Subject.query.limit(10).all()
    for subject in subjects:
        performances = StudentPerformance.query.filter_by(subject_id=subject.id).all()
        if performances:
            avg_marks = sum(p.final_internal for p in performances) / len(performances)
        else:
            avg_marks = 0
        
        subject_performance.append({
            'name': subject.name,
            'code': subject.code,
            'avg_marks': round(avg_marks, 1)
        })
    
    return render_template('principal/analytics.html',
                         dept_performance=dept_performance,
                         semester_performance=semester_performance,
                         risk_counts=risk_counts,
                         subject_performance=subject_performance,
                         now=datetime.now())


# =====================================================
# RISK MONITORING
# =====================================================

@principal_bp.route('/risk')
@login_required
@principal_required
def risk_monitoring():
    """Monitor students by risk level"""
    
    # Get filter parameters
    risk_filter = request.args.get('risk', 'all')
    dept_filter = request.args.get('department', 'all')
    sem_filter = request.args.get('semester', 'all')
    search_query = request.args.get('search', '')
    
    # Base query for students
    students_query = Student.query
    
    # Apply department filter
    if dept_filter != 'all':
        students_query = students_query.filter_by(department_id=int(dept_filter))
    
    # Apply semester filter
    if sem_filter != 'all':
        students_query = students_query.filter_by(current_semester=int(sem_filter))
    
    # Apply search filter
    if search_query:
        students_query = students_query.filter(
            db.or_(
                Student.name.ilike(f'%{search_query}%'),
                Student.registration_number.ilike(f'%{search_query}%'),
                Student.student_id.ilike(f'%{search_query}%')
            )
        )
    
    students = students_query.all()
    
    # Build student data with performances
    student_data = []
    risk_counts = {
        'Critical': 0,
        'High Risk': 0,
        'Average': 0,
        'Safe': 0,
        'Best': 0
    }
    
    for student in students:
        # Get latest performance for this student
        latest_perf = StudentPerformance.query.filter_by(
            student_id=student.id
        ).order_by(StudentPerformance.created_at.desc()).first()
        
        if latest_perf:
            subject = Subject.query.get(latest_perf.subject_id)
            
            # Calculate grade
            if latest_perf.final_internal >= 18:
                grade = 'A+'
            elif latest_perf.final_internal >= 15:
                grade = 'A'
            elif latest_perf.final_internal >= 12:
                grade = 'B'
            elif latest_perf.final_internal >= 10:
                grade = 'C'
            else:
                grade = 'D'
            
            # Apply risk filter
            if risk_filter != 'all' and latest_perf.risk_status != risk_filter:
                continue
            
            # Update risk counts
            if latest_perf.risk_status in risk_counts:
                risk_counts[latest_perf.risk_status] += 1
            
            student_data.append({
                'id': student.id,
                'student_id': student.student_id,
                'reg_number': student.registration_number,
                'name': student.name,
                'department': student.department.name if student.department else 'N/A',
                'semester': student.current_semester,
                'subject': subject.name if subject else 'N/A',
                'attendance': latest_perf.attendance,
                'marks': latest_perf.final_internal,
                'grade': grade,
                'risk': latest_perf.risk_status
            })
        else:
            # Student has no performance data
            if risk_filter != 'all' and risk_filter != 'No Data':
                continue
            
            student_data.append({
                'id': student.id,
                'student_id': student.student_id,
                'reg_number': student.registration_number,
                'name': student.name,
                'department': student.department.name if student.department else 'N/A',
                'semester': student.current_semester,
                'subject': 'No Data',
                'attendance': 0,
                'marks': 0,
                'grade': 'N/A',
                'risk': 'No Data'
            })
    
    # Get departments for filter dropdown
    departments = Department.query.all()
    
    # Get semesters for filter dropdown
    semesters = db.session.query(Student.current_semester).distinct().order_by(
        Student.current_semester
    ).all()
    semesters = [s[0] for s in semesters if s[0]]
    
    return render_template('principal/risk.html',
                         student_data=student_data,
                         departments=departments,
                         semesters=semesters,
                         risk_counts=risk_counts,
                         selected_risk=risk_filter,
                         selected_dept=dept_filter,
                         selected_sem=sem_filter,
                         now=datetime.now())


# =====================================================
# REPORTS PAGE (NEW)
# =====================================================

@principal_bp.route('/reports')
@login_required
@principal_required
def reports_page():
    """Reports page - Shows export options"""
    
    total_students = Student.query.count()
    total_teachers = User.query.filter_by(role='teacher', is_active=True).count()
    total_departments = Department.query.count()
    total_subjects = Subject.query.count()
    
    return render_template('principal/reports.html', 
                         total_students=total_students,
                         total_teachers=total_teachers,
                         total_departments=total_departments,
                         total_subjects=total_subjects,
                         now=datetime.now())


# =====================================================
# EXPORT REPORTS (CSV)
# =====================================================

@principal_bp.route('/export/student-performance')
@login_required
@principal_required
def export_student_performance():
    """Export student performance as CSV"""
    
    si = StringIO()
    cw = csv.writer(si)
    
    # Headers
    cw.writerow([
        'Registration No', 'Student Name', 'Department', 'Semester',
        'Subject', 'Internal 1', 'Internal 2', 'Seminar', 'Assessment',
        'Total Marks', 'Final Marks (/20)', 'Attendance %', 'Grade', 'Risk Status'
    ])
    
    # Get all performances
    performances = StudentPerformance.query.all()
    
    for perf in performances:
        student = Student.query.get(perf.student_id)
        subject = Subject.query.get(perf.subject_id)
        
        if not student or not subject:
            continue
        
        # Calculate grade
        grade = 'A+'
        if perf.final_internal >= 18:
            grade = 'A+'
        elif perf.final_internal >= 15:
            grade = 'A'
        elif perf.final_internal >= 12:
            grade = 'B'
        elif perf.final_internal >= 10:
            grade = 'C'
        else:
            grade = 'D'
        
        cw.writerow([
            student.registration_number,
            student.name,
            student.department.name if student.department else 'N/A',
            perf.semester,
            subject.name,
            perf.internal1,
            perf.internal2,
            perf.seminar,
            perf.assessment,
            perf.total_marks,
            perf.final_internal,
            perf.attendance,
            grade,
            perf.risk_status
        ])
    
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename=student_performance_{date.today()}.csv"
    output.headers["Content-type"] = "text/csv"
    
    return output


@principal_bp.route('/export/risk-report')
@login_required
@principal_required
def export_risk_report():
    """Export risk report as CSV"""
    
    si = StringIO()
    cw = csv.writer(si)
    
    # Headers
    cw.writerow([
        'Registration No', 'Student Name', 'Department', 'Semester',
        'Subject', 'Final Marks', 'Attendance %', 'Grade', 'Risk Status'
    ])
    
    # Get all performances
    performances = StudentPerformance.query.all()
    
    for perf in performances:
        student = Student.query.get(perf.student_id)
        subject = Subject.query.get(perf.subject_id)
        
        if not student or not subject:
            continue
        
        # Calculate grade
        grade = 'A+'
        if perf.final_internal >= 18:
            grade = 'A+'
        elif perf.final_internal >= 15:
            grade = 'A'
        elif perf.final_internal >= 12:
            grade = 'B'
        elif perf.final_internal >= 10:
            grade = 'C'
        else:
            grade = 'D'
        
        cw.writerow([
            student.registration_number,
            student.name,
            student.department.name if student.department else 'N/A',
            perf.semester,
            subject.name,
            perf.final_internal,
            perf.attendance,
            grade,
            perf.risk_status
        ])
    
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename=risk_report_{date.today()}.csv"
    output.headers["Content-type"] = "text/csv"
    
    return output


@principal_bp.route('/export/attendance-summary')
@login_required
@principal_required
def export_attendance_summary():
    """Export attendance summary as CSV"""
    
    si = StringIO()
    cw = csv.writer(si)
    
    # Headers
    cw.writerow([
        'Registration No', 'Student Name', 'Department', 'Semester',
        'Subject', 'Month', 'Year', 'Total Classes', 'Attended',
        'Attendance %', 'Penalty Amount', 'Penalty Status'
    ])
    
    # Get all attendance records
    attendance_records = Attendance.query.all()
    
    for att in attendance_records:
        student = Student.query.get(att.student_id)
        subject = Subject.query.get(att.subject_id)
        
        if not student or not subject:
            continue
        
        cw.writerow([
            student.registration_number,
            student.name,
            student.department.name if student.department else 'N/A',
            att.semester,
            subject.name,
            att.month,
            att.year,
            att.total_classes,
            att.attended_classes,
            att.attendance_percentage,
            att.penalty_amount,
            att.penalty_status
        ])
    
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename=attendance_summary_{date.today()}.csv"
    output.headers["Content-type"] = "text/csv"
    
    return output


# =====================================================
# ACADEMIC OVERVIEW
# =====================================================

@principal_bp.route('/academic-overview')
@login_required
@principal_required
def academic_overview():
    """Academic overview page"""
    
    # Get current academic year
    current_academic_year = AcademicYear.query.filter_by(is_current=True).first()
    
    # Determine active semester based on month
    today = date.today()
    if 6 <= today.month <= 11:  # June to November
        active_semester = "Odd Semester (1,3,5,7)"
    else:  # December to April
        active_semester = "Even Semester (2,4,6,8)"
    
    # Get upcoming exams (next 30 days)
    from datetime import timedelta
    next_month = today + timedelta(days=30)
    upcoming_exams = ExamTimetable.query.filter(
        ExamTimetable.exam_date >= today,
        ExamTimetable.exam_date <= next_month
    ).order_by(ExamTimetable.exam_date).limit(10).all()
    
    # Semester-wise statistics
    semester_stats = []
    for sem in range(1, 9):
        student_count = Student.query.filter_by(current_semester=sem).count()
        subject_count = Subject.query.filter_by(semester_id=sem).count()
        
        semester_stats.append({
            'semester': sem,
            'students': student_count,
            'subjects': subject_count
        })
    
    # Department-wise statistics
    dept_stats = []
    departments = Department.query.all()
    for dept in departments:
        student_count = Student.query.filter_by(department_id=dept.id).count()
        teacher_count = User.query.filter_by(role='teacher', department=dept.code).count()
        subject_count = Subject.query.filter_by(department_id=dept.id).count()
        
        dept_stats.append({
            'name': dept.name,
            'code': dept.code,
            'students': student_count,
            'teachers': teacher_count,
            'subjects': subject_count
        })
    
    return render_template('principal/academic_overview.html',
                         current_academic_year=current_academic_year.year if current_academic_year else '2025-2026',
                         active_semester=active_semester,
                         upcoming_exams=upcoming_exams,
                         semester_stats=semester_stats,
                         dept_stats=dept_stats,
                         now=datetime.now())


# =====================================================
# STUDENT DETAILS
# =====================================================

@principal_bp.route('/student-details/<int:student_id>')
@login_required
@principal_required
def student_details(student_id):
    """View complete student details"""
    student = Student.query.get_or_404(student_id)
    
    # Get all performances for this student
    performances = student.performances.order_by(
        StudentPerformance.semester,
        StudentPerformance.subject_id
    ).all()
    
    # Group performances by semester
    performances_by_semester = {}
    for perf in performances:
        subject = Subject.query.get(perf.subject_id)
        if perf.semester not in performances_by_semester:
            performances_by_semester[perf.semester] = []
        
        # Calculate grade
        grade = 'A+'
        if perf.final_internal >= 18:
            grade = 'A+'
        elif perf.final_internal >= 15:
            grade = 'A'
        elif perf.final_internal >= 12:
            grade = 'B'
        elif perf.final_internal >= 10:
            grade = 'C'
        else:
            grade = 'D'
        
        performances_by_semester[perf.semester].append({
            'subject': subject,
            'internal1': perf.internal1,
            'internal2': perf.internal2,
            'seminar': perf.seminar,
            'assessment': perf.assessment,
            'final_marks': perf.final_internal,
            'attendance': perf.attendance,
            'grade': grade,
            'risk': perf.risk_status
        })
    
    # Calculate semester summaries
    semester_summaries = []
    for sem in range(1, student.current_semester + 1):
        if sem in performances_by_semester:
            sem_perfs = performances_by_semester[sem]
            avg_marks = sum(p['final_marks'] for p in sem_perfs) / len(sem_perfs)
            avg_attendance = sum(p['attendance'] for p in sem_perfs) / len(sem_perfs)
            sgpa = (avg_marks / 20) * 10
            
            semester_summaries.append({
                'semester': sem,
                'subjects': len(sem_perfs),
                'avg_marks': round(avg_marks, 2),
                'avg_attendance': round(avg_attendance, 2),
                'sgpa': round(sgpa, 2)
            })
    
    # Calculate CGPA
    if semester_summaries:
        cgpa = sum(s['sgpa'] for s in semester_summaries) / len(semester_summaries)
    else:
        cgpa = 0
    
    return render_template('principal/student_details.html',
                         student=student,
                         performances_by_semester=performances_by_semester,
                         semester_summaries=semester_summaries,
                         cgpa=round(cgpa, 2),
                         now=datetime.now())