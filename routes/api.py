# routes/api.py
from flask import Blueprint, jsonify, session
from flask_login import current_user
from datetime import datetime, timedelta
from model import Notification
from extensions import db

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/notifications/unread-count')
def unread_notification_count():
    """Get unread notification count for current user based on role"""
    today = datetime.now().date()
    
    try:
        if current_user.is_authenticated:
            # For logged-in users: show 'all', 'public', and their specific role
            count = Notification.query.filter(
                Notification.is_active == True,
                Notification.start_date <= today,
                Notification.end_date >= today,
                db.or_(
                    Notification.target_role == 'all',
                    Notification.target_role == 'public',
                    Notification.target_role == current_user.role
                )
            ).count()
        else:
            # For public users: only show 'public' notifications
            count = Notification.query.filter(
                Notification.target_role == 'public',
                Notification.is_active == True,
                Notification.start_date <= today,
                Notification.end_date >= today
            ).count()
        
        return jsonify({'success': True, 'count': count})
    except Exception as e:
        print(f"Error in unread count: {e}")
        return jsonify({'success': True, 'count': 0})

@api_bp.route('/notifications/list')
def notification_list():
    """Get list of notifications for current user based on role"""
    today = datetime.now().date()
    
    try:
        if current_user.is_authenticated:
            # For logged-in users: show 'all', 'public', and their specific role
            notifications = Notification.query.filter(
                Notification.is_active == True,
                Notification.start_date <= today,
                Notification.end_date >= today,
                db.or_(
                    Notification.target_role == 'all',
                    Notification.target_role == 'public',
                    Notification.target_role == current_user.role
                )
            ).order_by(Notification.created_at.desc()).limit(20).all()
            
            result = []
            for notif in notifications:
                result.append({
                    'id': notif.id,
                    'title': notif.get_prefixed_title(),
                    'message': notif.get_prefixed_message(),
                    'type': notif.notification_type,
                    'is_read': False,  # Can implement read tracking later if needed
                    'time_ago': get_time_ago(notif.created_at),
                    'link': get_notification_link(notif, current_user.role),
                    'icon': get_icon_name(notif.notification_type),
                    'icon_class': notif.get_color_class()
                })
        else:
            # For public users: only show 'public' notifications
            notifications = Notification.query.filter(
                Notification.target_role == 'public',
                Notification.is_active == True,
                Notification.start_date <= today,
                Notification.end_date >= today
            ).order_by(Notification.created_at.desc()).limit(20).all()
            
            result = []
            for notif in notifications:
                result.append({
                    'id': notif.id,
                    'title': notif.get_prefixed_title(),
                    'message': notif.get_prefixed_message(),
                    'type': notif.notification_type,
                    'is_read': False,
                    'time_ago': get_time_ago(notif.created_at),
                    'link': get_public_notification_link(notif),
                    'icon': get_icon_name(notif.notification_type),
                    'icon_class': notif.get_color_class()
                })
        
        return jsonify({'success': True, 'notifications': result})
    except Exception as e:
        print(f"Error loading notifications: {e}")
        return jsonify({'success': True, 'notifications': []})

@api_bp.route('/notifications/latest')
def latest_notification():
    """Get latest notification for popup"""
    today = datetime.now().date()
    
    try:
        if current_user.is_authenticated:
            # For logged-in users: get latest from 'all', 'public', or their role
            notif = Notification.query.filter(
                Notification.is_active == True,
                Notification.start_date <= today,
                Notification.end_date >= today,
                db.or_(
                    Notification.target_role == 'all',
                    Notification.target_role == 'public',
                    Notification.target_role == current_user.role
                )
            ).order_by(Notification.created_at.desc()).first()
        else:
            # For public users: get latest public notification
            notif = Notification.query.filter(
                Notification.target_role == 'public',
                Notification.is_active == True,
                Notification.start_date <= today,
                Notification.end_date >= today
            ).order_by(Notification.created_at.desc()).first()
        
        if notif:
            return jsonify({
                'success': True,
                'notification': {
                    'id': notif.id,
                    'title': notif.get_prefixed_title(),
                    'message': notif.get_prefixed_message(),
                    'type': notif.notification_type,
                    'time_ago': get_time_ago(notif.created_at),
                    'link': get_public_notification_link(notif) if not current_user.is_authenticated else get_notification_link(notif, current_user.role),
                    'icon': get_icon_name(notif.notification_type),
                    'icon_class': notif.get_color_class()
                }
            })
        
        return jsonify({'success': True, 'notification': None})
    except Exception as e:
        print(f"Error in latest notification: {e}")
        return jsonify({'success': True, 'notification': None})

@api_bp.route('/notifications/<int:id>/read', methods=['POST'])
def mark_notification_read(id):
    """Mark a notification as read - For future implementation"""
    # You can implement read tracking later if needed
    return jsonify({'success': True})

@api_bp.route('/notifications/mark-all-read', methods=['POST'])
def mark_all_read():
    """Mark all notifications as read - For future implementation"""
    return jsonify({'success': True})

def get_time_ago(dt):
    """Convert datetime to time ago string"""
    if not dt:
        return "Just now"
    
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"

def get_icon_name(notification_type):
    """Get icon name for notification type"""
    icons = {
        'fee': 'fa-indian-rupee-sign',
        'meeting': 'fa-people-group',
        'event': 'fa-calendar-check',
        'result': 'fa-chart-simple',
        'timetable': 'fa-calendar-days',
        'holiday': 'fa-umbrella-beach',
        'emergency': 'fa-exclamation-triangle',
        'general': 'fa-bullhorn'
    }
    return icons.get(notification_type, 'fa-bell')

def get_notification_link(notification, role):
    """Get role-specific link for notification"""
    # Default links based on notification type and role
    if notification.notification_type == 'timetable':
        if role == 'student':
            return '/student/timetable'
        elif role == 'teacher':
            return '/teacher/dashboard'
        elif role == 'hod':
            return '/hod/dashboard'
        elif role == 'coordinator':
            return '/coordinator/timetable-view'
        elif role == 'principal':
            return '/principal/dashboard'
    
    elif notification.notification_type == 'result':
        if role == 'student':
            return '/student/results'
        else:
            return '/dashboard'
    
    elif notification.notification_type == 'fee':
        if role == 'student':
            return '/student/fees'
    
    # Default
    return '/'

def get_public_notification_link(notification):
    """Get link for public notifications"""
    if notification.notification_type == 'timetable':
        return '/public/exam-timetable'
    elif notification.notification_type == 'room':
        return '/public/room-allocation'
    elif notification.notification_type == 'invigilation':
        return '/public/invigilator'
    else:
        return '/public/notifications'