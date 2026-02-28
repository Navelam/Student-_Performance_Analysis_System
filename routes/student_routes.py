# routes/student_routes.py
from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from model import Notification
from model import QuestionPaper
from extensions import db
from model import (
    User, Student, Subject, StudentPerformance, 
    AcademicYear, Department
)
from datetime import datetime

student_bp = Blueprint('student', __name__, url_prefix='/student')

def student_required(f):
    """Decorator to restrict access to students only"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'student':
            flash('Access denied. Student privileges required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# =====================================================
# HELPER FUNCTIONS
# =====================================================

def calculate_grade(final_marks):
    """Calculate grade based on final marks (out of 20)"""
    if final_marks >= 18:
        return 'A+'
    elif final_marks >= 15:
        return 'A'
    elif final_marks >= 12:
        return 'B'
    elif final_marks >= 10:
        return 'C'
    else:
        return 'D'

def calculate_percentage(final_marks):
    """Calculate percentage from final marks"""
    return int((final_marks / 20) * 100)

def get_student_record(user_id):
    """Get student record for current user"""
    return Student.query.filter_by(user_id=user_id).first()

def get_feedback_by_risk(risk):
    """Get feedback message based on risk status"""
    feedback = {
        'Critical': {
            'message': 'You are in Critical level. Please concentrate more on your studies. Attend classes regularly.',
            'color': 'danger',
            'bg': '#dc3545',
            'text': 'white',
            'icon': 'exclamation-triangle'
        },
        'Average': {
            'message': 'You are Average. Try harder to improve. Focus on weak subjects.',
            'color': 'warning',
            'bg': '#ffc107',
            'text': '#2c3e50',
            'icon': 'exclamation-circle'
        },
        'Safe': {
            'message': 'You are Safe. Keep studying regularly. Maintain consistency.',
            'color': 'success',
            'bg': '#28a745',
            'text': 'white',
            'icon': 'check-circle'
        },
        'Best': {
            'message': 'Excellent Performance! Keep it up and aim higher.',
            'color': 'best',
            'bg': '#6f42c1',
            'text': 'white',
            'icon': 'star'
        }
    }
    return feedback.get(risk, feedback['Safe'])

# routes/student_routes.py - Update the dashboard function

@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    """Student dashboard with notifications and question papers"""
    student = get_student_record(current_user.id)
    
    if not student:
        flash('Student record not found', 'danger')
        return redirect(url_for('auth.logout'))
    
    # Get all performances for this student
    performances = StudentPerformance.query.filter_by(
        student_id=student.id
    ).all()
    
    # Calculate overall statistics
    total_attendance = 0
    total_marks = 0
    subject_count = len(performances)
    
    risk_counts = {'Critical': 0, 'Average': 0, 'Safe': 0, 'Best': 0}
    
    for perf in performances:
        total_attendance += perf.attendance
        total_marks += perf.final_internal
        risk_counts[perf.risk_status] = risk_counts.get(perf.risk_status, 0) + 1
    
    avg_attendance = round(total_attendance / subject_count, 1) if subject_count > 0 else 0
    avg_marks = round(total_marks / subject_count, 1) if subject_count > 0 else 0
    overall_grade = calculate_grade(avg_marks)
    
    # Determine overall risk based on average
    if avg_attendance < 70 or avg_marks < 10:
        overall_risk = 'Critical'
    elif avg_marks < 12:
        overall_risk = 'Average'
    elif avg_marks >= 18 and avg_attendance >= 90:
        overall_risk = 'Best'
    else:
        overall_risk = 'Safe'
    
    # Get active notifications for student
    today = datetime.now().date()
    notifications = Notification.query.filter(
        db.or_(
            Notification.target_role == 'student',
            Notification.target_role == 'all'
        ),
        Notification.is_active == True,
        Notification.start_date <= today,
        Notification.end_date >= today
    ).order_by(Notification.created_at.desc()).limit(10).all()
    
    # ===== NEW: Get question papers for student's subjects =====
    # Get the student's current semester and department
    current_semester = student.current_semester
    department_id = student.department_id
    
    # Get subjects for this student's current semester
    subjects_in_semester = Subject.query.filter_by(
        department_id=department_id,
        semester_id=current_semester
    ).all()
    
    subject_ids = [s.id for s in subjects_in_semester]
    
    # Get recent question papers for these subjects
    recent_papers = []
    if subject_ids:
        recent_papers = QuestionPaper.query.filter(
            QuestionPaper.subject_id.in_(subject_ids),
            QuestionPaper.is_active == True
        ).order_by(QuestionPaper.uploaded_at.desc()).limit(6).all()
    
    # Prepare chart data
    chart_labels = []
    chart_data = []
    chart_colors = []
    
    for perf in performances[:10]:
        subject = Subject.query.get(perf.subject_id)
        if subject:
            chart_labels.append(subject.name[:15] + ('...' if len(subject.name) > 15 else ''))
            chart_data.append(perf.final_internal)
            
            if perf.risk_status == 'Critical':
                chart_colors.append('#dc3545')
            elif perf.risk_status == 'Average':
                chart_colors.append('#ffc107')
            elif perf.risk_status == 'Safe':
                chart_colors.append('#28a745')
            else:
                chart_colors.append('#6f42c1')
    
    import json
    return render_template('student/dashboard.html',
                         student=student,
                         avg_attendance=avg_attendance,
                         avg_marks=avg_marks,
                         overall_grade=overall_grade,
                         overall_risk=overall_risk,
                         risk_counts=risk_counts,
                         notifications=notifications,
                         recent_papers=recent_papers,  # ← Add this line
                         chart_labels=json.dumps(chart_labels),
                         chart_data=json.dumps(chart_data),
                         chart_colors=json.dumps(chart_colors),
                         now=datetime.now())

# =====================================================
# STUDENT PERFORMANCE DETAILS (WITH DIRECT FEEDBACK)
# =====================================================

@student_bp.route('/performance')
@login_required
@student_required
def performance():
    """Detailed performance view with subject-wise feedback"""
    student = get_student_record(current_user.id)
    
    if not student:
        flash('Student record not found', 'danger')
        return redirect(url_for('auth.logout'))
    
    # Get all performances for this student
    performances = StudentPerformance.query.filter_by(
        student_id=student.id
    ).order_by(StudentPerformance.semester).all()
    
    # Prepare performance data with subject details and feedback
    performance_data = []
    for perf in performances:
        subject = Subject.query.get(perf.subject_id)
        if subject:
            percentage = calculate_percentage(perf.final_internal)
            grade = calculate_grade(perf.final_internal)
            
            # Get feedback based on risk
            feedback = get_feedback_by_risk(perf.risk_status)
            
            # Calculate marks needed for next grade
            if perf.final_internal >= 18:
                next_grade = "A+ (Max)"
                marks_needed = 0
            elif perf.final_internal >= 15:
                next_grade = "A+"
                marks_needed = round(18 - perf.final_internal, 1)
            elif perf.final_internal >= 12:
                next_grade = "A"
                marks_needed = round(15 - perf.final_internal, 1)
            elif perf.final_internal >= 10:
                next_grade = "B"
                marks_needed = round(12 - perf.final_internal, 1)
            else:
                next_grade = "C (Pass)"
                marks_needed = round(10 - perf.final_internal, 1)
            
            performance_data.append({
                'id': perf.id,
                'subject': subject,
                'internal1': perf.internal1,
                'internal2': perf.internal2,
                'seminar': perf.seminar,
                'assessment': perf.assessment,
                'attendance': perf.attendance,
                'final_marks': perf.final_internal,
                'percentage': percentage,
                'grade': grade,
                'risk_status': perf.risk_status,
                'semester': perf.semester,
                'feedback': feedback,
                'next_grade': next_grade,
                'marks_needed': marks_needed
            })
    
    # Group by semester
    performances_by_semester = {}
    for perf in performance_data:
        sem = perf['semester']
        if sem not in performances_by_semester:
            performances_by_semester[sem] = []
        performances_by_semester[sem].append(perf)
    
    return render_template('student/performance.html',
                         student=student,
                         performances=performance_data,
                         performances_by_semester=performances_by_semester,
                         now=datetime.now())


# =====================================================
# STUDENT NOTIFICATIONS (OPTIONAL - CAN BE REMOVED)
# =====================================================

@student_bp.route('/notifications')
@login_required
@student_required
def notifications():
    """Redirect to performance page since we're using direct feedback"""
    return redirect(url_for('student.performance'))


# =====================================================
# API ENDPOINTS
# =====================================================

@student_bp.route('/api/performance-summary')
@login_required
@student_required
def performance_summary():
    """API endpoint for performance summary charts"""
    student = get_student_record(current_user.id)
    
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    # Get performances
    performances = StudentPerformance.query.filter_by(
        student_id=student.id
    ).all()
    
    # Prepare data
    subjects = []
    marks = []
    attendance = []
    colors = []
    
    for perf in performances[:10]:
        subject = Subject.query.get(perf.subject_id)
        if subject:
            subjects.append(subject.name[:15])
            marks.append(perf.final_internal)
            attendance.append(perf.attendance)
            
            if perf.risk_status == 'Critical':
                colors.append('#dc3545')
            elif perf.risk_status == 'Average':
                colors.append('#ffc107')
            elif perf.risk_status == 'Safe':
                colors.append('#28a745')
            else:
                colors.append('#6f42c1')
    
    return jsonify({
        'subjects': subjects,
        'marks': marks,
        'attendance': attendance,
        'colors': colors
    })
    
# routes/student_routes.py - Updated dashboard

@student_bp.route('/my-performance')
@login_required
@student_required
def my_performance():
    """Student view all semesters performance"""
    student = get_student_record(current_user.id)
    
    if not student:
        flash('Student record not found', 'danger')
        return redirect(url_for('auth.logout'))
    
    current_semester = student.current_semester
    
    # Get ALL performances
    performances = StudentPerformance.query.filter_by(
        student_id=student.id
    ).order_by(StudentPerformance.semester).all()
    
    # Group by semester
    performances_by_semester = {}
    for perf in performances:
        subject = Subject.query.get(perf.subject_id)
        if perf.semester not in performances_by_semester:
            performances_by_semester[perf.semester] = []
        
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
            'marks': perf.final_internal,
            'attendance': perf.attendance,
            'grade': grade,
            'risk': perf.risk_status,
            'is_current': perf.semester == current_semester
        })
    
    # Calculate semester summaries
    semester_summaries = []
    for sem in range(1, current_semester + 1):
        if sem in performances_by_semester:
            sem_marks = [p['marks'] for p in performances_by_semester[sem]]
            avg_marks = sum(sem_marks) / len(sem_marks)
            sgpa = (avg_marks / 20) * 10
            semester_summaries.append({
                'semester': sem,
                'avg_marks': round(avg_marks, 2),
                'sgpa': round(sgpa, 2),
                'subjects': len(sem_marks),
                'is_current': sem == current_semester
            })
    
    # Calculate CGPA
    all_marks = [p.final_internal for p in performances]
    cgpa = (sum(all_marks) / len(all_marks) / 20) * 10 if all_marks else 0
    
    return render_template('student/my_performance.html',
                         student=student,
                         current_semester=current_semester,
                         performances_by_semester=performances_by_semester,
                         semester_summaries=semester_summaries,
                         cgpa=round(cgpa, 2))
# =====================================================
# STUDENT QUESTION PAPERS
# =====================================================

@student_bp.route('/question-papers')
@login_required
@student_required
def question_papers():
    """View all question papers for student's subjects"""
    student = get_student_record(current_user.id)
    
    if not student:
        flash('Student record not found', 'danger')
        return redirect(url_for('auth.logout'))
    
    # Get student's department and semester
    department_id = student.department_id
    current_semester = student.current_semester
    
    # Get all semesters the student has studied (1 to current)
    semesters = range(1, current_semester + 1)
    
    # Get subjects for these semesters
    subjects = Subject.query.filter(
        Subject.department_id == department_id,
        Subject.semester_id.in_(semesters)
    ).all()
    
    subject_ids = [s.id for s in subjects]
    
    # Get question papers for these subjects
    papers = QuestionPaper.query.filter(
        QuestionPaper.subject_id.in_(subject_ids),
        QuestionPaper.is_active == True
    ).order_by(QuestionPaper.uploaded_at.desc()).all()
    
    # Group by subject
    papers_by_subject = {}
    for paper in papers:
        subject = Subject.query.get(paper.subject_id)
        if subject:
            if subject.id not in papers_by_subject:
                papers_by_subject[subject.id] = {
                    'subject': subject,
                    'papers': []
                }
            papers_by_subject[subject.id]['papers'].append(paper)
    
    return render_template('student/question_papers.html',
                         student=student,
                         papers_by_subject=papers_by_subject,
                         subjects=subjects)

@student_bp.route('/download-question-paper/<int:paper_id>')
@login_required
@student_required
def download_question_paper(paper_id):
    """Download a question paper"""
    paper = QuestionPaper.query.get_or_404(paper_id)
    
    # Verify student has access to this subject
    student = get_student_record(current_user.id)
    
    if not student:
        flash('Student record not found', 'danger')
        return redirect(url_for('auth.logout'))
    
    subject = Subject.query.get(paper.subject_id)
    
    # Check if this subject belongs to student's department and semester <= current
    if (subject.department_id != student.department_id or 
        subject.semester_id > student.current_semester):
        flash('You are not authorized to download this paper', 'danger')
        return redirect(url_for('student.dashboard'))
    
    from flask import send_file
    import os
    
    if not os.path.exists(paper.file_path):
        flash('File not found', 'danger')
        return redirect(url_for('student.question_papers'))
    
    return send_file(
        paper.file_path,
        as_attachment=True,
        download_name=paper.file_name,
        mimetype='application/octet-stream'
    )