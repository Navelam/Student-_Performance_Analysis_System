# routes/public_routes.py
from flask import Blueprint, render_template
from model import ExamTimetable, ExamRoomAllocation, InvigilatorAssignment
from model import db, Notification
from datetime import datetime
from extensions import db

public_bp = Blueprint('public', __name__)
@public_bp.route('/')
def index():
    """Public index page with public announcements"""
    today = datetime.now().date()
    
    # Get public notifications (target_role = 'all')
    public_notifications = Notification.query.filter(
        Notification.target_role == 'all',
        Notification.is_active == True,
        Notification.start_date <= today,
        Notification.end_date >= today
    ).order_by(Notification.created_at.desc()).limit(5).all()
    
    return render_template('index.html', 
                         public_notifications=public_notifications,
                         now=datetime.now())
    
@public_bp.route('/exam-timetable')
def exam_timetable():
    """Public view for exam timetable"""
    exams = ExamTimetable.query.order_by(
        ExamTimetable.exam_date,
        ExamTimetable.exam_time
    ).all()
    
    grouped = {}
    for exam in exams:
        date_str = exam.exam_date.strftime('%Y-%m-%d')
        if date_str not in grouped:
            grouped[date_str] = {
                'date': exam.exam_date,
                'exams': []
            }
        grouped[date_str]['exams'].append(exam)
    
    return render_template('public/exam_timetable.html', grouped=grouped)

@public_bp.route('/room-allocation')
def room_allocation():
    """Public view for room allocations"""
    allocations = ExamRoomAllocation.query.order_by(
        ExamRoomAllocation.exam_date,
        ExamRoomAllocation.exam_time,
        ExamRoomAllocation.room_number
    ).all()
    
    grouped = {}
    for alloc in allocations:
        date_str = alloc.exam_date.strftime('%Y-%m-%d')
        if date_str not in grouped:
            grouped[date_str] = {
                'date': alloc.exam_date,
                'rooms': []
            }
        grouped[date_str]['rooms'].append(alloc)
    
    return render_template('public/room_allocation.html', grouped=grouped)

@public_bp.route('/invigilator')
def invigilator():
    """Public view for invigilator assignments"""
    assignments = InvigilatorAssignment.query.order_by(
        InvigilatorAssignment.exam_date,
        InvigilatorAssignment.exam_time,
        InvigilatorAssignment.room_number
    ).all()
    
    grouped = {}
    for inv in assignments:
        date_str = inv.exam_date.strftime('%Y-%m-%d')
        if date_str not in grouped:
            grouped[date_str] = {
                'date': inv.exam_date,
                'assignments': []
            }
        grouped[date_str]['assignments'].append(inv)
    
    return render_template('public/invigilator.html', grouped=grouped)

@public_bp.route('/notifications')
def notifications():
    """Public view for notifications"""
    return render_template('public/notifications.html')