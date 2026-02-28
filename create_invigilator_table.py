# create_invigilator_table.py
from app import create_app
from extensions import db
from model import InvigilatorAssignment

app = create_app('development')

with app.app_context():
    # Create the table
    db.create_all()
    print(" InvigilatorAssignment table created successfully!")
    
    # Verify it exists
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    if 'invigilator_assignments' in tables:
        print(" Table verified in database")
    else:
        print(" Table not found")