# model.py
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db 

def calculate_current_semester(admission_year):
    """
    Calculate current semester based on admission year and current date
    
    Rules:
    - Odd semesters (1,3,5,7): June to December
    - Even semesters (2,4,6,8): January to April
    - Each year has 2 semesters
    - Max semester is 8
    """
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    # Calculate years since admission
    years_passed = current_year - admission_year
    
    # Determine current semester type based on month
    if 6 <= current_month <= 12:  # June to December (Odd semesters)
        semester = (years_passed * 2) + 1
    else:  # January to April (Even semesters)
        semester = (years_passed * 2) + 2
    
    # Cap at 8 semesters (4 years)
    return min(semester, 8)

# =====================================================
# USER NOTIFICATION MODEL
# =====================================================

class UserNotification(db.Model):
    """Tracks which notifications users have read"""
    __tablename__ = 'user_notifications'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    notification_id = db.Column(db.Integer, db.ForeignKey('notifications.id'), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Add this relationship
    notification = db.relationship('Notification', backref='user_notifications')
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'notification_id', name='unique_user_notification'),
        {'extend_existing': True}
    )
    
    # Property for start_date
    @property
    def start_date(self):
        """Proxy property to get start_date from associated notification"""
        return self.notification.start_date if self.notification else None
    
    # Property for end_date
    @property
    def end_date(self):
        """Proxy property to get end_date from associated notification"""
        return self.notification.end_date if self.notification else None
    
    # Property for notification_type
    @property
    def notification_type(self):
        """Proxy property to get notification_type from associated notification"""
        return self.notification.notification_type if self.notification else 'general'
    
    # Property for target_role
    @property
    def target_role(self):
        """Proxy property to get target_role from associated notification"""
        return self.notification.target_role if self.notification else None
    
    def get_color(self):
        """Proxy method to get color from associated notification"""
        if self.notification:
            return self.notification.get_color()
        return '#6f42c1'
    
    def get_icon(self):
        """Proxy method to get icon from associated notification"""
        if self.notification:
            return self.notification.get_icon()
        return 'fa-solid fa-bell'
    
    def get_prefixed_title(self):
        """Proxy method to get prefixed title from associated notification"""
        if self.notification:
            return self.notification.get_prefixed_title()
        return 'Notification'
    
    def get_prefixed_message(self):
        """Proxy method to get prefixed message from associated notification"""
        if self.notification:
            return self.notification.get_prefixed_message()
        return ''
    
    def __repr__(self):
        return f'<UserNotification user_id={self.user_id} notification_id={self.notification_id} read={self.is_read}>'

# =====================================================
# NOTIFICATION MODEL
# =====================================================

class Notification(db.Model):
    """Notification Model - Managed by Coordinator"""
    __tablename__ = 'notifications'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False, default='general')
    target_role = db.Column(db.String(20), nullable=False, default='all')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    link = db.Column(db.String(500), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships - Will be linked after User is defined
    target_user = None
    creator = None
    
    def to_dict(self):
        """Convert notification to dictionary for display"""
        return {
            'id': self.id,
            'title': self.get_prefixed_title(),
            'message': self.get_prefixed_message(),
            'notification_type': self.notification_type,
            'target_role': self.target_role,
            'link': self.link,
            'is_read': self.is_read,
            'is_active': self.is_active,
            'start_date': self.start_date.strftime('%d-%m-%Y') if self.start_date else None,
            'end_date': self.end_date.strftime('%d-%m-%Y') if self.end_date else None,
            'created_at': self.created_at.strftime('%d-%m-%Y %H:%M'),
            'time_ago': self.get_time_ago(),
            'icon': self.get_icon(),
            'color': self.get_color(),
            'color_class': self.get_color_class()
        }
    
    def get_prefixed_title(self):
        """Get title with appropriate prefix based on type"""
        prefixes = {
            'fee': 'Fee Reminder',
            'meeting': 'Parents Meeting',
            'event': 'College Event',
            'result': 'Results Published',
            'timetable': 'Exam Timetable',
            'academic': 'Academic Update',
            'general': 'Announcement'
        }
        return prefixes.get(self.notification_type, 'Announcement') + ': ' + (self.title or '')
    
    def get_prefixed_message(self):
        """Get message with automatic prefix based on type"""
        prefixes = {
            'fee': "Please pay your semester fees before due date. ",
            'meeting': "Parents are requested to attend the scheduled meeting. ",
            'event': "All students are invited to participate. ",
            'result': "Exam results have been published. ",
            'timetable': "Exam timetable has been released. ",
            'academic': "College academic schedule update. ",
            'general': ""
        }
        return prefixes.get(self.notification_type, "") + (self.message or '')
    
    def get_icon(self):
        """Get Font Awesome icon for notification type"""
        icons = {
            'fee': 'fa-solid fa-indian-rupee-sign',
            'meeting': 'fa-solid fa-people-group',
            'event': 'fa-solid fa-calendar-check',
            'result': 'fa-solid fa-chart-simple',
            'timetable': 'fa-solid fa-calendar-days',
            'academic': 'fa-solid fa-school',
            'general': 'fa-solid fa-bullhorn',
            'room': 'fa-solid fa-door-open',
            'invigilation': 'fa-solid fa-user-tie',
            'exam': 'fa-solid fa-pencil-alt'
        }
        return icons.get(self.notification_type, 'fa-solid fa-bell')
    
    def get_color(self):
        """Get hex color for notification type"""
        colors = {
            'fee': '#dc3545',
            'meeting': '#fd7e14',
            'event': '#6f42c1',
            'result': '#28a745',
            'timetable': '#17a2b8',
            'academic': '#20c997',
            'general': '#6610f2'
        }
        return colors.get(self.notification_type, '#6f42c1')
    
    def get_color_class(self):
        """Get Bootstrap color class for notification type"""
        classes = {
            'fee': 'danger',
            'meeting': 'warning',
            'event': 'purple',
            'result': 'success',
            'timetable': 'info',
            'academic': 'teal',
            'general': 'indigo'
        }
        return classes.get(self.notification_type, 'primary')
    
    def get_time_ago(self):
        """Get human readable time difference"""
        if not self.created_at:
            return "Just now"
        now = datetime.utcnow()
        diff = now - self.created_at
        
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
    
    def __repr__(self):
        return f'<Notification {self.id}: {self.title} ({self.notification_type})>'

# =====================================================
# TEACHER SUBJECT MODEL
# =====================================================

class TeacherSubject(db.Model):
    __tablename__ = "teacher_subjects"
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_years.id'), nullable=False)
    semester_id = db.Column(db.Integer, db.ForeignKey('semesters.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    teacher = None
    subject = None
    academic_year = None
    semester = None

# =====================================================
# USER MODEL
# =====================================================

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    teacher_subjects = db.relationship('TeacherSubject', back_populates='teacher', lazy=True)
    created_notifications = db.relationship('Notification', foreign_keys='Notification.created_by', back_populates='creator', lazy=True)
    user_notifications = db.relationship('UserNotification', backref='notification_user', lazy=True)
    hod_department = db.relationship('Department', back_populates='hod', foreign_keys='Department.hod_id')
    student_record = db.relationship('Student', back_populates='user', uselist=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.id)
    
    def __repr__(self):
        return f'<User {self.username}>'

# =====================================================
# DEPARTMENT MODEL
# =====================================================

class Department(db.Model):
    __tablename__ = "departments"
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    hod_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    hod = db.relationship('User', foreign_keys=[hod_id], back_populates='hod_department')
    courses = db.relationship('Course', back_populates='department', lazy=True)
    subjects = db.relationship('Subject', back_populates='department', lazy=True)
    students = db.relationship('Student', back_populates='department', lazy=True)

# =====================================================
# COURSE MODEL
# =====================================================

class Course(db.Model):
    __tablename__ = "courses"
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), nullable=False)
    duration_years = db.Column(db.Integer, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    department = db.relationship('Department', back_populates='courses')
    semesters = db.relationship('Semester', back_populates='course', lazy=True)
    students = db.relationship('Student', back_populates='course', lazy=True)

# =====================================================
# ACADEMIC YEAR MODEL
# =====================================================

class AcademicYear(db.Model):
    __tablename__ = "academic_years"
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.String(20), unique=True, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_current = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    semesters = db.relationship('Semester', back_populates='academic_year', lazy=True)
    performances = db.relationship('StudentPerformance', back_populates='academic_year', lazy=True)

# =====================================================
# SEMESTER MODEL
# =====================================================

class Semester(db.Model):
    __tablename__ = "semesters"
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    semester_number = db.Column(db.Integer, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_years.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    course = db.relationship('Course', back_populates='semesters')
    academic_year = db.relationship('AcademicYear', back_populates='semesters')
    subjects = db.relationship('Subject', back_populates='semester', lazy=True)

# =====================================================
# SUBJECT MODEL
# =====================================================

class Subject(db.Model):
    __tablename__ = "subjects"
    
    __table_args__ = (
        db.UniqueConstraint('code', name='unique_subject_code'),
        db.UniqueConstraint('department_id', 'semester_id', 'name', name='unique_subject_per_semester'),
        {'extend_existing': True}
    )
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    code = db.Column(db.String(20), nullable=False)
    credits = db.Column(db.Integer, default=3)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    semester_id = db.Column(db.Integer, db.ForeignKey('semesters.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    department = db.relationship('Department', back_populates='subjects')
    semester = db.relationship('Semester', back_populates='subjects')
    teacher_assignments = db.relationship('TeacherSubject', back_populates='subject', lazy=True)
    student_performances = db.relationship('StudentPerformance', back_populates='subject', lazy=True)
    
    def __repr__(self):
        return f"<Subject {self.code} - {self.name}>"

# =====================================================
# STUDENT MODEL
# =====================================================

class Student(db.Model):
    __tablename__ = "students"
    
    id = db.Column(db.Integer, primary_key=True)
    registration_number = db.Column(db.String(20), unique=True, nullable=False)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    admission_year = db.Column(db.Integer, nullable=False)
    admission_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='student_record')
    course = db.relationship('Course', back_populates='students')
    department = db.relationship('Department', back_populates='students')
    performances = db.relationship('StudentPerformance', back_populates='student', lazy='dynamic')
    attendance_records = db.relationship('Attendance', back_populates='student', lazy='dynamic')
    
    @property
    def current_semester(self):
        return calculate_current_semester(self.admission_year)
    
    def get_max_semester(self):
        max_perf = self.performances.order_by(StudentPerformance.semester.desc()).first()
        return max_perf.semester if max_perf else 0
    
    def get_available_semesters(self):
        return list(range(1, self.current_semester + 1))
    
    def __repr__(self):
        return f"<Student {self.name} ({self.registration_number}) - Admission {self.admission_year}>"

# =====================================================
# STUDENT PERFORMANCE MODEL
# =====================================================

class StudentPerformance(db.Model):
    __tablename__ = "student_performances"
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_years.id'), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    attendance = db.Column(db.Float, nullable=False, default=0)
    internal1 = db.Column(db.Float, nullable=False, default=0)
    internal2 = db.Column(db.Float, nullable=False, default=0)
    seminar = db.Column(db.Float, nullable=False, default=0)
    assessment = db.Column(db.Float, nullable=False, default=0)
    total_marks = db.Column(db.Float, nullable=False, default=0)
    final_internal = db.Column(db.Float, nullable=False, default=0)
    risk_status = db.Column(db.String(20), nullable=False, default='Safe')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', back_populates='performances')
    subject = db.relationship('Subject', back_populates='student_performances')
    academic_year = db.relationship('AcademicYear', back_populates='performances')
    
    __table_args__ = (
        db.UniqueConstraint('student_id', 'subject_id', 'semester', name='unique_student_subject_semester'),
    )
    
    def is_current_semester(self):
        return self.semester == self.student.current_semester
    
    def __repr__(self):
        return f'<Performance Student:{self.student_id} Sem:{self.semester}>'

# =====================================================
# EXAM TIMETABLE MODEL
# =====================================================

class ExamTimetable(db.Model):
    """Exam Timetable Model - Whole College System"""
    __tablename__ = 'exam_timetables'
    
    __table_args__ = (
        db.UniqueConstraint('subject_id', 'academic_year', name='unique_subject_per_year'),
        {'extend_existing': True}
    )
    
    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    exam_date = db.Column(db.Date, nullable=False)
    exam_time = db.Column(db.String(10), nullable=False)
    academic_year = db.Column(db.String(20), nullable=False)
    exam_cycle = db.Column(db.String(10), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='Generated')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    department = db.relationship('Department', backref='exam_timetables')
    subject = db.relationship('Subject', backref='exam_timetables')
    creator = db.relationship('User', backref='created_timetables')
    
    def __repr__(self):
        subject_code = self.subject.code if self.subject else "No Subject"
        return f"<ExamTimetable {subject_code} - {self.exam_date} {self.exam_time}>"

# =====================================================
# EXAM ROOM ALLOCATION MODEL
# =====================================================

class ExamRoomAllocation(db.Model):
    """Room allocation for exams - one per room per session"""
    __tablename__ = 'exam_room_allocations'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    exam_date = db.Column(db.Date, nullable=False)
    exam_time = db.Column(db.String(10), nullable=False)
    block = db.Column(db.String(1), nullable=False)
    room_number = db.Column(db.String(10), nullable=False)
    capacity = db.Column(db.Integer, default=20)
    total_students = db.Column(db.Integer, default=0)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by], backref='room_allocations')
    seating = db.relationship('SeatingArrangement', backref='room_allocation',
                              foreign_keys='SeatingArrangement.room_allocation_id',
                              cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('exam_date', 'exam_time', 'room_number', name='unique_room_per_session'),
        {'extend_existing': True}
    )
    
    @property
    def room_display(self):
        return f"{self.block}{self.room_number}"
    
    def __repr__(self):
        return f'<Room {self.block}{self.room_number} - {self.exam_date} {self.exam_time}>'

# =====================================================
# SEATING ARRANGEMENT MODEL
# =====================================================

class SeatingArrangement(db.Model):
    """Individual student seating per exam session"""
    __tablename__ = 'seating_arrangements'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    room_allocation_id = db.Column(db.Integer, db.ForeignKey('exam_room_allocations.id'), nullable=False)
    exam_date = db.Column(db.Date, nullable=False)
    exam_time = db.Column(db.String(10), nullable=False)
    block = db.Column(db.String(1), nullable=False)
    room_number = db.Column(db.String(10), nullable=False)
    seat_number = db.Column(db.Integer, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    reg_number = db.Column(db.String(20), nullable=False)
    student_name = db.Column(db.String(150), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref='seating_assignments', foreign_keys=[student_id])
    
    __table_args__ = (
        db.UniqueConstraint('room_allocation_id', 'seat_number', name='unique_seat_per_room'),
        db.UniqueConstraint('exam_date', 'exam_time', 'student_id', name='unique_student_per_session'),
        {'extend_existing': True}
    )
    
    def __repr__(self):
        return f'<Seat {self.block}{self.room_number}-{self.seat_number}: {self.reg_number}>'

# =====================================================
# INVIGILATOR ASSIGNMENT MODEL
# =====================================================

class InvigilatorAssignment(db.Model):
    """Invigilator assignment for exam rooms"""
    __tablename__ = 'invigilator_assignments'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    exam_date = db.Column(db.Date, nullable=False)
    exam_time = db.Column(db.String(10), nullable=False)
    block = db.Column(db.String(1), nullable=False)
    room_number = db.Column(db.String(10), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    teacher_name = db.Column(db.String(150), nullable=False)
    teacher_department = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='Assigned')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref='invigilation_duties')
    
    __table_args__ = (
        db.UniqueConstraint('exam_date', 'exam_time', 'room_number', name='unique_invigilator_per_room'),
        {'extend_existing': True}
    )

# =====================================================
# ATTENDANCE MODEL
# =====================================================

class Attendance(db.Model):
    __tablename__ = "attendance"
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_classes = db.Column(db.Integer, nullable=False, default=0)
    attended_classes = db.Column(db.Integer, nullable=False, default=0)
    attendance_percentage = db.Column(db.Integer, nullable=False, default=0)
    penalty_amount = db.Column(db.Integer, nullable=False, default=0)
    penalty_status = db.Column(db.String(20), nullable=False, default='No Penalty')
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    predicted_attendance_trend = db.Column(db.Float, nullable=True)
    risk_of_dropout = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', back_populates='attendance_records')
    subject = db.relationship('Subject', backref='attendance_records')
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref='attendance_taken')
    
    __table_args__ = (
        db.UniqueConstraint('student_id', 'subject_id', 'month', 'year', name='unique_attendance_per_month'),
        {'extend_existing': True}
    )
    
    def calculate_penalty(self):
        if self.attendance_percentage >= 75:
            self.penalty_amount = 0
            self.penalty_status = 'No Penalty'
        elif self.attendance_percentage >= 70:
            self.penalty_amount = 200
            self.penalty_status = 'Low Penalty'
        elif self.attendance_percentage >= 60:
            self.penalty_amount = 500
            self.penalty_status = 'Medium Penalty'
        else:
            self.penalty_amount = 1000
            self.penalty_status = 'High Penalty'
        return self.penalty_amount

# =====================================================
# QUESTION PAPER MODEL
# =====================================================

# In model.py, make sure the QuestionPaper model is complete:

class QuestionPaper(db.Model):
    __tablename__ = "question_papers"
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    exam_type = db.Column(db.String(20), nullable=False)  # 'internal1', 'internal2', 'semester', 'model'
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(255), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=True)  # in bytes
    answer_key_path = db.Column(db.String(255), nullable=True)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    semester = db.Column(db.Integer, nullable=True)
    academic_year = db.Column(db.String(20), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    subject = db.relationship('Subject', backref=db.backref('question_papers', lazy=True))
    uploader = db.relationship('User', foreign_keys=[uploaded_by], backref='uploaded_papers')
    
    def __repr__(self):
        return f'<QuestionPaper {self.title} - {self.exam_type}>'
    
    def get_file_icon(self):
        """Get Font Awesome icon based on file extension"""
        ext = self.file_name.split('.')[-1].lower() if '.' in self.file_name else ''
        icons = {
            'pdf': 'fa-file-pdf',
            'doc': 'fa-file-word',
            'docx': 'fa-file-word',
            'txt': 'fa-file-alt',
            'jpg': 'fa-file-image',
            'jpeg': 'fa-file-image',
            'png': 'fa-file-image'
        }
        return icons.get(ext, 'fa-file')
    
    def get_file_size_display(self):
        """Return human readable file size"""
        if not self.file_size:
            return 'Unknown'
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024.0:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024.0
        return f"{self.file_size:.1f} TB"

# =====================================================
# SET RELATIONSHIPS
# =====================================================

# Set Notification relationships
Notification.target_user = db.relationship('User', foreign_keys=[Notification.user_id], backref='personal_notifications')
Notification.creator = db.relationship('User', foreign_keys=[Notification.created_by], back_populates='created_notifications')

# Set TeacherSubject relationships
TeacherSubject.teacher = db.relationship('User', back_populates='teacher_subjects')
TeacherSubject.subject = db.relationship('Subject', back_populates='teacher_assignments')
TeacherSubject.academic_year = db.relationship('AcademicYear')
TeacherSubject.semester = db.relationship('Semester')

# Set Student relationships
Student.user = db.relationship('User', back_populates='student_record')
Student.course = db.relationship('Course', back_populates='students')
Student.department = db.relationship('Department', back_populates='students')
Student.performances = db.relationship('StudentPerformance', back_populates='student', lazy=True)


from flask_login import UserMixin

class UnifiedUser(UserMixin):
    """Unified user class that works for both CSV and database users"""
    
    def __init__(self, source='database', **kwargs):
        self.source = source
        
        if source == 'database':
            # For database users
            self.id = str(kwargs.get('id'))
            self.username = kwargs.get('username')
            self.role = kwargs.get('role')
            self.full_name = kwargs.get('full_name')
            self.email = kwargs.get('email')
            self.department = kwargs.get('department')
            self.phone = kwargs.get('phone')
            
        elif source == 'csv':
            # For CSV users
            user_data = kwargs.get('user_data', {})
            role = kwargs.get('role')
            username = kwargs.get('username')
            
            self.id = str(user_data.get('employee_id') or user_data.get('register_no') or username)
            self.username = username
            self.role = role
            self.full_name = user_data.get('full_name') or user_data.get('name', '')
            self.email = user_data.get('email', '')
            self.phone = user_data.get('phone', '')
            self.department = user_data.get('department', '')
            
            # Student specific
            if role == 'student':
                self.register_no = user_data.get('register_no', '')
                self.year = user_data.get('year', '')
                self.semester = user_data.get('semester', '')
            
            # Teacher/HOD specific
            if role in ['teacher', 'hod']:
                self.employee_id = user_data.get('employee_id', '')
    
    def get_id(self):
        return str(self.id)
    
    def get_department(self):
        return self.department