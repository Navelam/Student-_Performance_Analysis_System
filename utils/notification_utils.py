from model import Notification, UserNotification, User
from extensions import db
from datetime import datetime

def assign_notification_to_users(notification_id, target_role):
    """Assign a notification to all users of a specific role"""
    
    notification = Notification.query.get(notification_id)
    if not notification:
        return 0
    
    # Determine which users to notify
    if target_role == 'all':
        users = User.query.filter_by(is_active=True).all()
    elif target_role == 'students':
        users = User.query.filter_by(role='student', is_active=True).all()
    elif target_role == 'teachers':
        users = User.query.filter_by(role='teacher', is_active=True).all()
    elif target_role == 'hod':
        users = User.query.filter_by(role='hod', is_active=True).all()
    elif target_role == 'coordinator':
        users = User.query.filter_by(role='coordinator', is_active=True).all()
    elif target_role == 'principal':
        users = User.query.filter_by(role='principal', is_active=True).all()
    elif target_role == 'public':
        # Public notifications don't need user assignments
        return 0
    else:
        users = []
    
    # Assign to each user
    assigned_count = 0
    for user in users:
        # Check if already assigned (avoid duplicates)
        existing = UserNotification.query.filter_by(
            user_id=user.id,
            notification_id=notification.id
        ).first()
        
        if not existing:
            user_notification = UserNotification(
                user_id=user.id,
                notification_id=notification.id,
                is_read=False,
                created_at=datetime.utcnow()
            )
            db.session.add(user_notification)
            assigned_count += 1
    
    db.session.commit()
    return assigned_count