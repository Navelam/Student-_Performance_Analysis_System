"""
Notification Helper Utility
Provides functions to create and manage notifications throughout the application
"""

from model import Notification, db, User
from flask_login import current_user
from datetime import datetime, timedelta, date
import json

class NotificationHelper:
    """Helper class for creating and managing notifications"""
    
    @staticmethod
    def create_notification(target_role, title, message, notification_type, user_id=None, link=None):
        """
        Create a single notification
        
        Args:
            target_role: Role to receive notification (student, teacher, hod, coordinator, principal, all)
            title: Notification title
            message: Notification message
            notification_type: Type of notification (exam, room, marks, etc.)
            user_id: Specific user ID (optional)
            link: URL to redirect when clicked
        
        Returns:
            Notification object or None if failed
        """
        try:
            notification = Notification(
                target_role=target_role,  # ← CHANGED FROM user_role TO target_role
                user_id=user_id,
                title=title,
                message=message,
                link=link,
                notification_type=notification_type,
                start_date=date.today(),
                end_date=date(date.today().year, 12, 31),
                created_at=datetime.utcnow(),
                is_active=True,
                is_read=False
            )
            db.session.add(notification)
            db.session.commit()
            return notification
        except Exception as e:
            db.session.rollback()
            print(f"Error creating notification: {e}")
            return None
    
    @staticmethod
    def create_bulk_notifications(target_roles, title, message, notification_type, link=None):
        """
        Create notifications for multiple roles at once
        
        Args:
            target_roles: List of roles (e.g., ['student', 'teacher'])
            title: Notification title
            message: Notification message
            notification_type: Type of notification
            link: URL to redirect when clicked
        
        Returns:
            Number of notifications created
        """
        notifications = []
        for role in target_roles:
            notification = Notification(
                target_role=role,  # ← CHANGED FROM user_role TO target_role
                title=title,
                message=message,
                link=link,
                notification_type=notification_type,
                start_date=date.today(),
                end_date=date(date.today().year, 12, 31),
                created_at=datetime.utcnow(),
                is_active=True,
                is_read=False
            )
            notifications.append(notification)
        
        try:
            db.session.bulk_save_objects(notifications)
            db.session.commit()
            return len(notifications)
        except Exception as e:
            db.session.rollback()
            print(f"Error creating bulk notifications: {e}")
            return 0
    
    @staticmethod
    def create_notification_for_all(title, message, notification_type, link=None):
        """Create notification for all users"""
        return NotificationHelper.create_bulk_notifications(
            ['student', 'teacher', 'hod', 'coordinator', 'principal'],
            title, message, notification_type, link
        )
    
    @staticmethod
    def get_unread_count(user):
        """Get unread notification count for current user"""
        if not user or not user.is_authenticated:
            return 0
        
        # Build query based on user role
        query = Notification.query.filter(
            db.or_(
                Notification.target_role == 'all',
                Notification.target_role == user.role,
                Notification.user_id == user.id
            )
        ).filter(Notification.is_read == False)
        
        return query.count()
    
    @staticmethod
    def get_latest_unread(user):
        """Get latest unread notification for popup"""
        if not user or not user.is_authenticated:
            return None
        
        return Notification.query.filter(
            db.or_(
                Notification.target_role == 'all',
                Notification.target_role == user.role,
                Notification.user_id == user.id
            )
        ).filter(Notification.is_read == False)\
         .order_by(Notification.created_at.desc())\
         .first()
    
    @staticmethod
    def get_user_notifications(user, limit=50):
        """Get all notifications for user"""
        if not user or not user.is_authenticated:
            return []
        
        return Notification.query.filter(
            db.or_(
                Notification.target_role == 'all',
                Notification.target_role == user.role,
                Notification.user_id == user.id
            )
        ).order_by(Notification.created_at.desc())\
         .limit(limit)\
         .all()
    
    @staticmethod
    def mark_as_read(notification_id, user):
        """Mark a specific notification as read"""
        notification = Notification.query.get(notification_id)
        if notification:
            # Check if user has permission to mark this notification
            if (notification.user_id and notification.user_id == user.id) or \
               (notification.target_role in ['all', user.role] and not notification.user_id):
                notification.is_read = True
                notification.read_at = datetime.utcnow()
                db.session.commit()
                return True
        return False
    
    @staticmethod
    def mark_all_as_read(user):
        """Mark all notifications as read for user"""
        query = Notification.query.filter(
            db.or_(
                Notification.target_role == 'all',
                Notification.target_role == user.role,
                Notification.user_id == user.id
            )
        ).filter(Notification.is_read == False)
        
        count = query.update({'is_read': True, 'read_at': datetime.utcnow()}, synchronize_session=False)
        db.session.commit()
        return count
    
    @staticmethod
    def delete_old_notifications(days=30):
        """Delete notifications older than specified days"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        count = Notification.query.filter(Notification.created_at < cutoff).delete()
        db.session.commit()
        return count


# Event-based notification creators

def notify_exam_timetable_published(academic_year, exam_cycle, department_id=None):
    """Create notification when exam timetable is published"""
    title = f"📅 Exam Timetable Published"
    message = f"Exam timetable for {academic_year} ({exam_cycle}) has been published."
    link = "/public/exam-timetable"
    
    if department_id:
        # Notify only specific department
        students = User.query.filter_by(role='student', department_id=department_id).all()
        teachers = User.query.filter_by(role='teacher', department_id=department_id).all()
        
        for student in students:
            NotificationHelper.create_notification(
                target_role='student',  # ← CHANGED
                user_id=student.id,
                title=title,
                message=message,
                notification_type='exam',
                link=link
            )
        
        for teacher in teachers:
            NotificationHelper.create_notification(
                target_role='teacher',  # ← CHANGED
                user_id=teacher.id,
                title=title,
                message=message,
                notification_type='exam',
                link=link
            )
        
        # Notify HOD
        hod = User.query.filter_by(role='hod', department_id=department_id).first()
        if hod:
            NotificationHelper.create_notification(
                target_role='hod',  # ← CHANGED
                user_id=hod.id,
                title=title,
                message=message,
                notification_type='exam',
                link=link
            )
    else:
        # Notify all students and teachers
        NotificationHelper.create_bulk_notifications(
            ['student', 'teacher', 'hod'],
            title, message, 'exam', link
        )

def notify_room_allocation_completed(exam_date, department_id=None):
    """Create notification when room allocation is completed"""
    title = f"🏢 Room Allocation Completed"
    message = f"Room allocation for exams on {exam_date} has been completed."
    link = "/public/room-allocation"
    
    if department_id:
        students = User.query.filter_by(role='student', department_id=department_id).all()
        for student in students:
            NotificationHelper.create_notification(
                target_role='student',
                user_id=student.id,
                title=title,
                message=message,
                notification_type='room',
                link=link
            )
    else:
        NotificationHelper.create_bulk_notifications(
            ['student', 'teacher'], title, message, 'room', link
        )

def notify_invigilator_assigned(teacher_id, teacher_name, exam_date, room_number, exam_time):
    """Create notification when invigilator is assigned"""
    title = f"👨‍🏫 Invigilation Duty Assigned"
    message = f"You have been assigned as invigilator for Room {room_number} on {exam_date} at {exam_time}."
    link = "/teacher/dashboard"
    
    return NotificationHelper.create_notification(
        target_role='teacher',  # ← CHANGED
        user_id=teacher_id,
        title=title,
        message=message,
        notification_type='invigilation',
        link=link
    )

def notify_marks_uploaded(subject_name, semester, teacher_name, department_id):
    """Create notification when marks are uploaded"""
    title = f"📊 Internal Marks Uploaded"
    message = f"Internal marks for {subject_name} (Semester {semester}) have been uploaded by {teacher_name}."
    link = "/student/performance"
    
    students = User.query.filter_by(role='student', department_id=department_id).all()
    
    count = 0
    for student in students:
        notif = NotificationHelper.create_notification(
            target_role='student',  # ← CHANGED
            user_id=student.id,
            title=title,
            message=message,
            notification_type='marks',
            link=link
        )
        if notif:
            count += 1
    
    # Also notify HOD
    hod = User.query.filter_by(role='hod', department_id=department_id).first()
    if hod:
        NotificationHelper.create_notification(
            target_role='hod',  # ← CHANGED
            user_id=hod.id,
            title=title,
            message=message,
            notification_type='marks',
            link="/hod/performance-analysis"
        )
    
    return count

def notify_results_published(academic_year, department_id=None):
    """Create notification when results are published"""
    title = f"🎓 Results Published"
    message = f"Results for {academic_year} have been published. Check your performance."
    link = "/student/performance"
    
    if department_id:
        students = User.query.filter_by(role='student', department_id=department_id).all()
        for student in students:
            NotificationHelper.create_notification(
                target_role='student',  # ← CHANGED
                user_id=student.id,
                title=title,
                message=message,
                notification_type='results',
                link=link
            )
    else:
        NotificationHelper.create_bulk_notifications(
            ['student'], title, message, 'results', link
        )

def notify_low_attendance(student_id, student_name, subject_name, attendance_percent):
    """Create notification for low attendance"""
    title = f"⚠️ Low Attendance Alert"
    message = f"Your attendance in {subject_name} is {attendance_percent}%. Please improve to avoid penalty."
    link = "/student/performance"
    
    return NotificationHelper.create_notification(
        target_role='student',  # ← CHANGED
        user_id=student_id,
        title=title,
        message=message,
        notification_type='attendance',
        link=link
    )

def notify_risk_alert(student_id, student_name, subject_name, risk_status):
    """Create notification for risk alert"""
    title = f"⚠️ {risk_status} Alert"
    message = f"You are at {risk_status} level in {subject_name}. Please contact your teacher."
    link = "/student/performance"
    
    return NotificationHelper.create_notification(
        target_role='student',  # ← CHANGED
        user_id=student_id,
        title=title,
        message=message,
        notification_type='attendance',
        link=link
    )

def notify_announcement(title, message, link=None, target_roles=None):
    """Create announcement notification"""
    if target_roles is None:
        target_roles = ['student', 'teacher', 'hod', 'coordinator', 'principal']
    
    return NotificationHelper.create_bulk_notifications(
        target_roles, title, message, 'announcement', link
    )