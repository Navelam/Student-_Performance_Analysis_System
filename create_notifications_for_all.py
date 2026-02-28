# create_notifications_for_all.py
from app import create_app
from model import Notification, UserNotification, User
from datetime import datetime, date
from extensions import db

app = create_app()
with app.app_context():
    # Check if we already have notifications
    existing = Notification.query.first()
    if existing:
        print(f"Found {Notification.query.count()} existing notifications")
        choice = input("Delete existing and create new? (y/n): ")
        if choice.lower() == 'y':
            UserNotification.query.delete()
            Notification.query.delete()
            db.session.commit()
            print("Deleted existing notifications")
    
    # Create sample notifications
    notifications = [
        {
            'title': 'Welcome to SPAS',
            'message': 'Welcome to Student Performance Analysis System. Check your dashboard for updates.',
            'type': 'general',
            'target': 'all'
        },
        {
            'title': 'Exam Timetable Published',
            'message': 'The exam timetable for even semester 2025-2026 has been published.',
            'type': 'timetable',
            'target': 'all'
        },
        {
            'title': 'Parent-Teacher Meeting',
            'message': 'Parent-teacher meeting scheduled for March 15, 2026 at 10:00 AM in the Auditorium.',
            'type': 'meeting',
            'target': 'all'
        },
        {
            'title': 'Fee Reminder',
            'message': 'Last date for fee payment is March 31, 2026. Pay online to avoid late fee.',
            'type': 'fee',
            'target': 'students'
        },
        {
            'title': 'College Cultural Fest',
            'message': 'Annual cultural fest registrations are now open. Register by March 20.',
            'type': 'event',
            'target': 'all'
        }
    ]
    
    created_count = 0
    for n in notifications:
        notif = Notification(
            title=n['title'],
            message=n['message'],
            notification_type=n['type'],
            target_role=n['target'],
            start_date=date.today(),
            end_date=date(2026, 12, 31),
            created_by=1,  # Assuming admin ID 1
            is_active=True
        )
        db.session.add(notif)
        created_count += 1
    
    db.session.commit()
    print(f" Created {created_count} notifications")
    
    # Assign to ALL users
    users = User.query.all()
    notifications = Notification.query.all()
    
    assigned = 0
    for user in users:
        for notif in notifications:
            # Check if already assigned
            existing = UserNotification.query.filter_by(
                user_id=user.id,
                notification_id=notif.id
            ).first()
            
            if not existing:
                un = UserNotification(
                    user_id=user.id,
                    notification_id=notif.id,
                    is_read=False
                )
                db.session.add(un)
                assigned += 1
    
    db.session.commit()
    print(f" Assigned {assigned} notifications to {len(users)} users")
    
    print("\n" + "="*50)
    print("NOTIFICATION SYSTEM IS NOW READY!")
    print("="*50)
    print("\nLogin and click the bell icon to see notifications.")