"""
Safe database initialization with proper path handling
"""
import os
import sys

# Set absolute path for database (outside project for security)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_directory = os.path.join(os.path.dirname(BASE_DIR), 'mmuinsight_data')

# Create directory if it doesn't exist
os.makedirs(db_directory, exist_ok=True)

# Set the database path before importing app
os.environ['DATABASE_PATH'] = os.path.join(db_directory, 'mmuinsight.db')

# Now import app and initialize
from app import app, db
from extensions import bcrypt
from models import User, Subject, Review, Reply, Report

with app.app_context():
    db.create_all()
    print("[OK] Database initialized with new schema")
    
    test_accounts = [
        {'email': 'owner@mmu.edu.my', 'password': 'password123', 'user_type': 'admin', 'role': 'OWNER'},
        {'email': 'admin@mmu.edu.my', 'password': 'password123', 'user_type': 'admin', 'role': 'ADMIN'},
        {'email': 'mod@mmu.edu.my', 'password': 'password123', 'user_type': 'admin', 'role': 'MOD'},
        {'email': 'dr.smith@mmu.edu.my', 'password': 'password123', 'user_type': 'lecturer'},
        {'email': 'prof.johnson@mmu.edu.my', 'password': 'password123', 'user_type': 'lecturer'},
        {'email': 'dr.williams@mmu.edu.my', 'password': 'password123', 'user_type': 'lecturer'},
        {'email': 'ali.hassan@student.mmu.edu.my', 'password': 'password123', 'user_type': 'student'},
        {'email': 'sarah.khan@student.mmu.edu.my', 'password': 'password123', 'user_type': 'student'},
        {'email': 'rajesh.kumar@student.mmu.edu.my', 'password': 'password123', 'user_type': 'student'},
    ]
    
    for account in test_accounts:
        existing = User.query.filter_by(email=account['email']).first()
        if not existing:
            user = User(
                email=account['email'],
                password_hash=bcrypt.generate_password_hash(account['password']).decode('utf-8'),
                user_type=account['user_type'],
                role=account.get('role'),
                is_verified=True
            )
            db.session.add(user)
    
    db.session.commit()
    print("[OK] Test accounts created")
    print("\nTest Account Credentials (password: password123):")
    print("\nOwner:")
    print("  - owner@mmu.edu.my")
    print("\nAdmins:")
    print("  - admin@mmu.edu.my")
    print("\nMODs:")
    print("  - mod@mmu.edu.my")
    print("\nLecturers:")
    print("  - dr.smith@mmu.edu.my")
    print("  - prof.johnson@mmu.edu.my")
    print("  - dr.williams@mmu.edu.my")
    print("\nStudents:")
    print("  - ali.hassan@student.mmu.edu.my")
    print("  - sarah.khan@student.mmu.edu.my")
    print("  - rajesh.kumar@student.mmu.edu.my")
