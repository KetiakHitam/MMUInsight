from app import app, db
from models import User
from extensions import bcrypt

with app.app_context():
    # Drop all existing tables
    db.drop_all()
    
    # Create all tables
    db.create_all()
    
    # Create accounts - all use password123
    accounts = [
        # Admin accounts
        ("owner@mmu.edu.my", "lecturer", "OWNER", "password123"),
        ("admin@mmu.edu.my", "lecturer", "ADMIN", "password123"),
        ("mod@mmu.edu.my", "lecturer", "MOD", "password123"),
        # Lecturer accounts
        ("dr.smith@mmu.edu.my", "lecturer", None, "password123"),
        ("prof.johnson@mmu.edu.my", "lecturer", None, "password123"),
        ("dr.williams@mmu.edu.my", "lecturer", None, "password123"),
        # Student accounts
        ("ali.hassan@student.mmu.edu.my", "student", None, "password123"),
        ("sarah.khan@student.mmu.edu.my", "student", None, "password123"),
        ("rajesh.kumar@student.mmu.edu.my", "student", None, "password123"),
    ]
    
    for email, user_type, role, password in accounts:
        user = User(
            email=email,
            user_type=user_type,
            role=role,
            is_verified=True,
            is_claimed=(user_type == "lecturer")
        )
        user.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        db.session.add(user)
    
    db.session.commit()
    
    print("✓ Database initialized!")
    print("\nAll accounts use password: password123")
    print("\n📋 Accounts created:")
    print("\n  Owners:")
    print("    • owner@mmu.edu.my")
    print("\n  Admins:")
    print("    • admin@mmu.edu.my")
    print("\n  Moderators:")
    print("    • mod@mmu.edu.my")
    print("\n  Lecturers:")
    print("    • dr.smith@mmu.edu.my")
    print("    • prof.johnson@mmu.edu.my")
    print("    • dr.williams@mmu.edu.my")
    print("\n  Students:")
    print("    • ali.hassan@student.mmu.edu.my")
    print("    • sarah.khan@student.mmu.edu.my")
    print("    • rajesh.kumar@student.mmu.edu.my")
