from app import app, db
from models import User
from extensions import bcrypt

with app.app_context():
    db.create_all()
    
    # Create OWNER account
    owner = User(email="owner@mmu.edu.my", user_type="lecturer", role="OWNER", is_verified=True, is_claimed=True)
    owner.password_hash = bcrypt.generate_password_hash("owner123")
    db.session.add(owner)
    
    # Create ADMIN account
    admin = User(email="admin@mmu.edu.my", user_type="lecturer", role="ADMIN", is_verified=True, is_claimed=True)
    admin.password_hash = bcrypt.generate_password_hash("admin123")
    db.session.add(admin)
    
    # Create MOD account
    mod = User(email="mod@mmu.edu.my", user_type="lecturer", role="MOD", is_verified=True, is_claimed=True)
    mod.password_hash = bcrypt.generate_password_hash("mod123")
    db.session.add(mod)
    
    # Create lecturer account
    lecturer = User(email="lecturer@mmu.edu.my", user_type="lecturer", is_verified=True, is_claimed=True)
    lecturer.password_hash = bcrypt.generate_password_hash("lecturer123")
    db.session.add(lecturer)
    
    # Create student account
    student = User(email="student@mmu.edu.my", user_type="student", is_verified=True)
    student.password_hash = bcrypt.generate_password_hash("student123")
    db.session.add(student)
    
    db.session.commit()
    print("MMU accounts created!")
    print("owner@mmu.edu.my / owner123")
    print("admin@mmu.edu.my / admin123")
    print("mod@mmu.edu.my / mod123")
    print("lecturer@mmu.edu.my / lecturer123")
    print("student@mmu.edu.my / student123")
