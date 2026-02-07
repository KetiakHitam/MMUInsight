"""Fresh database initialization - for fixing schema issues locally"""
import os
import sys

# Delete old database file completely
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'mmuinsight.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)

if os.path.exists(db_path):
    os.remove(db_path)
    print(f"Deleted old database")

# Now import and create fresh - this will create all tables from models with bio column
from app import app, db

with app.app_context():
    db.create_all()
    print(f"Fresh DB created at {db_path} with all tables from models")

