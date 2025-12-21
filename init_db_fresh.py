from app import app, db
from extensions import bcrypt
from models import User, Subject, Review, Reply, Report

# Create all tables with the new schema
with app.app_context():
    db.create_all()
    print("✓ Database initialized with new schema")
    
    # Create test accounts
    test_accounts = [
        # Lecturers
        {'email': 'dr.smith@mmu.edu.my', 'password': 'password123', 'user_type': 'lecturer'},
        {'email': 'prof.johnson@mmu.edu.my', 'password': 'password123', 'user_type': 'lecturer'},
        {'email': 'dr.williams@mmu.edu.my', 'password': 'password123', 'user_type': 'lecturer'},
        # Admin
        {'email': 'admin@mmu.edu.my', 'password': 'password123', 'user_type': 'admin'},
        # Students
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
                is_verified=True
            )
            db.session.add(user)
    
    db.session.commit()
    print("✓ Test accounts created")
    print("\nTest Account Credentials (password: password123):")
    print("\nLecturers:")
    print("  - dr.smith@mmu.edu.my")
    print("  - prof.johnson@mmu.edu.my")
    print("  - dr.williams@mmu.edu.my")
    print("\nAdmin:")
    print("  - admin@mmu.edu.my")
    print("\nStudents:")
    print("  - ali.hassan@student.mmu.edu.my")
    print("  - sarah.khan@student.mmu.edu.my")
    print("  - rajesh.kumar@student.mmu.edu.my")
