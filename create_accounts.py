from app import app, db
from models import User
from extensions import bcrypt

with app.app_context():
    db.create_all()
    
    # Create MOD account
    mod = User(email="mod@test.com", user_type="lecturer", role="MOD", is_verified=True)
    mod.password_hash = bcrypt.generate_password_hash("mod123")
    db.session.add(mod)
    
    # Create ADMIN account
    admin = User(email="admin@test.com", user_type="lecturer", role="ADMIN", is_verified=True)
    admin.password_hash = bcrypt.generate_password_hash("admin123")
    db.session.add(admin)
    
    # Create OWNER account
    owner = User(email="owner@test.com", user_type="lecturer", role="OWNER", is_verified=True)
    owner.password_hash = bcrypt.generate_password_hash("owner123")
    db.session.add(owner)
    
    # Create lecturer account
    lecturer = User(email="lecturer@test.com", user_type="lecturer", is_verified=True)
    lecturer.password_hash = bcrypt.generate_password_hash("lecturer123")
    db.session.add(lecturer)
    
    # Create student account
    student = User(email="student@test.com", user_type="student", is_verified=True)
    student.password_hash = bcrypt.generate_password_hash("student123")
    db.session.add(student)
    
    db.session.commit()
    print("All accounts created!")
