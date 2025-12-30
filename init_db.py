from app import app, db
from models import User
from extensions import bcrypt

with app.app_context():
    # Drop all existing tables
    db.drop_all()
    
    # Create all tables
    db.create_all()
    
    # Create accounts - password = role name
    accounts = [
        ("owner@mmu.edu.my", "lecturer", "OWNER", "owner"),
        ("admin@mmu.edu.my", "lecturer", "ADMIN", "admin"),
        ("mod@mmu.edu.my", "lecturer", "MOD", "mod"),
        ("lecturer@mmu.edu.my", "lecturer", None, "lecturer"),
        ("student@mmu.edu.my", "student", None, "student"),
    ]
    
    for email, user_type, role, password in accounts:
        user = User(
            email=email,
            user_type=user_type,
            role=role,
            is_verified=True,
            is_claimed=(user_type == "lecturer")
        )
        user.password_hash = bcrypt.generate_password_hash(password)
        db.session.add(user)
    
    db.session.commit()
    
    print("✓ Database initialized!")
    print("\nAccounts created:")
    for email, user_type, role, password in accounts:
        role_display = f" ({role})" if role else ""
        print(f"  {email}{role_display} / {password}")
