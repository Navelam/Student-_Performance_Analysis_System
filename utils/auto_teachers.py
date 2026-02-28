# utils/auto_teachers.py
"""
Auto Teacher Generation Script
Creates teachers for all departments
"""

import sys
from pathlib import Path
from werkzeug.security import generate_password_hash

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from extensions import db
from model import User, Department

# Department mapping
DEPARTMENTS = [
    ("Computer Science", "CS"),
    ("Computer Applications", "CA"),
    ("Commerce Finance", "CF"),
    ("Commerce Co-op", "CC"),
    ("English", "EN"),
    ("Economics", "EC"),
    ("History", "HY")
]

# Teacher names by department
TEACHER_NAMES = {
    "CS": [
        "Dr. Arjun Sharma", "Prof. Priya Verma", "Dr. Rajesh Kumar",
        "Prof. Anjali Patel", "Dr. Suresh Reddy", "Prof. Deepa Gupta"
    ],
    "CA": [
        "Dr. Lakshmi Narayan", "Prof. Karthik Rao", "Dr. Divya Menon",
        "Prof. Anand Mishra", "Dr. Shweta Yadav", "Prof. Prakash Jha"
    ],
    "CF": [
        "Dr. Venkatesh Iyer", "Prof. Radhika Krishnan", "Dr. Gopal Desai",
        "Prof. Shanta Shah", "Dr. Ramesh Trivedi", "Prof. Latha Acharya"
    ],
    "CC": [
        "Dr. Meena Deshmukh", "Prof. Rajan Kulkarni", "Dr. Sunil Patil",
        "Prof. Asha More", "Dr. Dilip Pawar", "Prof. Shobha Jadhav"
    ],
    "EN": [
        "Dr. Susan Fernandez", "Prof. Michael D'Souza", "Dr. Jennifer Pereira",
        "Prof. Thomas Gonsalves", "Dr. Mary Rodrigues", "Prof. Joseph D'Costa"
    ],
    "EC": [
        "Dr. Abdul Khan", "Prof. Fatima Ansari", "Dr. Imran Sheikh",
        "Prof. Ayesha Begum", "Dr. Salman Ali", "Prof. Nargis Ahmed"
    ],
    "HY": [
        "Dr. Rajendra Nayak", "Prof. Shanta Sahoo", "Dr. Pradeep Mahapatra",
        "Prof. Sulochana Swain", "Dr. Bikram Behera", "Prof. Kanak Parida"
    ]
}

def generate_teachers():
    """Generate teachers for all departments"""
    print("\n" + "=" * 60)
    print("AUTO TEACHER GENERATION")
    print("=" * 60)
    
    app = create_app('development')
    
    with app.app_context():
        created_total = 0
        
        for dept_name, dept_code in DEPARTMENTS:
            print(f"\n📚 Creating teachers for {dept_name}...")
            
            teacher_names = TEACHER_NAMES.get(dept_code, [])
            
            for i, teacher_name in enumerate(teacher_names, 1):
                username = f"{dept_code.lower()}_teacher{i}"
                
                # Check if already exists
                existing = User.query.filter_by(username=username).first()
                if existing:
                    print(f"   ⏩ {username} already exists, skipping...")
                    continue
                
                # Create teacher
                teacher = User(
                    username=username,
                    email=f"{username}@college.edu",
                    full_name=teacher_name,
                    role='teacher',
                    department=dept_code,
                    password_hash=generate_password_hash('teacher123'),
                    is_active=True
                )
                db.session.add(teacher)
                created_total += 1
                print(f"   ✅ Created: {username}")
            
            db.session.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ SUCCESS: Created {created_total} teachers across all departments!")
        print("=" * 60)
        
        # Show summary
        print("\n📊 Summary by Department:")
        for dept_name, dept_code in DEPARTMENTS:
            count = User.query.filter_by(role='teacher', department=dept_code).count()
            print(f"   {dept_name}: {count} teachers")
        
        print("\n🔑 Login credentials:")
        print("   Username: [dept_code]_teacher[number] (e.g., cs_teacher1)")
        print("   Password: teacher123")

if __name__ == "__main__":
    generate_teachers()