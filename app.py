from flask import Flask, render_template
from config import config
from extensions import db, login_manager, migrate, mail, csrf  # Added csrf
import os
from datetime import datetime
import gc

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Make sure SECRET_KEY is set
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    csrf.init_app(app)  # Added this line
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from model import User
        return User.query.get(int(user_id))
    
    # FIXED: Proper indentation for debug_csrf
    @app.before_request
    def debug_csrf():
        from flask import session
        # Convert to string and encode properly
        session_str = str(session).encode('ascii', errors='ignore').decode('ascii')
        print(f"Session: {session_str}")
        print(f"CSRF token in session: {session.get('_csrf_token')}")
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    # =====================================================
    # HOME PAGE - Root URL
    # =====================================================
    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/index')
    def index():
        return render_template('index.html')
    
    # Context processors for templates
    @app.context_processor
    def utility_processor():
        return {'now': datetime.now()}
    
    @app.context_processor
    def inject_csrf_token():
        from flask_wtf.csrf import generate_csrf
        return dict(csrf_token=generate_csrf)
    
    @app.after_request
    def after_request(response):
        gc.collect()
        return response
    
    # Create upload directories
    with app.app_context():
        upload_dir = app.config.get('UPLOAD_FOLDER', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        os.makedirs(os.path.join(upload_dir, 'profile_pics'), exist_ok=True)
        os.makedirs(os.path.join(upload_dir, 'question_papers'), exist_ok=True)
    
    # Import and register blueprints (MOVED INSIDE THE FUNCTION)
    from routes.auth_routes import auth_bp
    from routes.principal_routes import principal_bp
    from routes.hod_routes import hod_bp
    from routes.teacher_routes import teacher_bp
    from routes.student_routes import student_bp
    from routes.coordinator_routes import coordinator_bp
    from routes.public_routes import public_bp
    from routes.api import api_bp  # Add this line
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(principal_bp, url_prefix='/principal')
    app.register_blueprint(hod_bp, url_prefix='/hod')
    app.register_blueprint(teacher_bp, url_prefix='/teacher')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(coordinator_bp, url_prefix='/coordinator')
    app.register_blueprint(public_bp, url_prefix='/public')
    app.register_blueprint(api_bp, url_prefix='/api')  # Add this line
    
    # Create tables
    with app.app_context():
        from model import (
            User, Department, Course, AcademicYear, Semester, 
            Subject, TeacherSubject, Student, StudentPerformance,
            Notification, UserNotification, ExamTimetable,
            InvigilatorAssignment, Attendance, QuestionPaper,
            ExamRoomAllocation, SeatingArrangement
        )
        
        db.create_all()
        print(" Database tables created/verified")
    
    return app

if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True, host='0.0.0.0', port=5000)