# utils/notification_triggers.py
from routes.notification_routes import create_notification
from model import User, Student
from datetime import datetime

class NotificationTriggers:
    
    @staticmethod
    def exam_timetable_published(academic_year, published_by):
        """Trigger when exam timetable is published"""
        create_notification(
            role='all',
            title='📅 Exam Timetable Published',
            message=f'Exam timetable for {academic_year} has been published. Please check the schedule.',
            type='info',
            url='/coordinator/timetable-view'
        )
    
    @staticmethod
    def room_allocation_completed(exam_date, allocated_by):
        """Trigger when room allocation is completed"""
        create_notification(
            role='student',
            title='🏢 Rooms Allocated',
            message=f'Exam rooms for {exam_date} have been allocated. Check your seating arrangement.',
            type='success',
            url='/student/exam-rooms'
        )
    
    @staticmethod
    def invigilator_duty_assigned(teacher_id, exam_date, room_number):
        """Trigger when invigilator is assigned"""
        create_notification(
            user_id=teacher_id,
            title='👨‍🏫 Invigilation Duty Assigned',
            message=f'You have been assigned as invigilator for Room {room_number} on {exam_date}.',
            type='info',
            url='/teacher/invigilation-duties'
        )
    
    @staticmethod
    def marks_uploaded(subject_name, semester, teacher_name):
        """Trigger when marks are uploaded"""
        create_notification(
            role='student',
            title='📊 Internal Marks Uploaded',
            message=f'Marks for {subject_name} (Semester {semester}) have been uploaded by {teacher_name}.',
            type='success',
            url='/student/performance'
        )
    
    @staticmethod
    def results_published(exam_type, semester):
        """Trigger when results are published"""
        create_notification(
            role='student',
            title='📋 Results Published',
            message=f'{exam_type} results for Semester {semester} have been published.',
            type='success',
            url='/student/results'
        )
    
    @staticmethod
    def low_attendance_alert(student_id, subject_name, attendance_percentage):
        """Trigger for low attendance alert"""
        student = Student.query.get(student_id)
        if student:
            create_notification(
                user_id=student.user_id,
                title='⚠️ Low Attendance Alert',
                message=f'Your attendance in {subject_name} is {attendance_percentage}%. Please attend classes regularly.',
                type='warning',
                url='/student/attendance'
            )
    
    @staticmethod
    def risk_alert(student_id, subject_name, risk_status):
        """Trigger for academic risk alert"""
        student = Student.query.get(student_id)
        if student:
            create_notification(
                user_id=student.user_id,
                title=f'🚨 {risk_status} Risk Alert',
                message=f'You have been marked as {risk_status} in {subject_name}. Please contact your teacher.',
                type='danger',
                url='/student/performance'
            )
    
    @staticmethod
    def meeting_reminder(meeting_title, date, time, venue, target_role='teacher'):
        """Trigger for meeting reminders"""
        create_notification(
            role=target_role,
            title='📢 Staff Meeting Reminder',
            message=f'{meeting_title} on {date} at {time} in {venue}.',
            type='info',
            url='/calendar'
        )
    
    @staticmethod
    def holiday_announcement(holiday_name, date, description):
        """Trigger for holiday announcements"""
        create_notification(
            role='all',
            title=f'🏖️ Holiday: {holiday_name}',
            message=f'{description} College will remain closed on {date}.',
            type='info'
        )
    
    @staticmethod
    def fee_due_reminder(student_id, due_date, amount):
        """Trigger for fee due reminders"""
        student = Student.query.get(student_id)
        if student:
            create_notification(
                user_id=student.user_id,
                title='💰 Fee Due Reminder',
                message=f'Your fee payment of ₹{amount} is due on {due_date}. Please pay before due date.',
                type='warning',
                url='/student/fees'
            )