"""
Production-safe database initialization script.
Safe to run on every deployment - preserves all existing data.

- Creates tables only if they don't exist
- Seeds 681 lecturers from scraped_lecturers.txt only if Lecturer table is empty
- Creates default admin accounts only if User table is empty
- Idempotent: can be run multiple times without data loss
"""

import re
from app import app, db
from models import User, Lecturer
from extensions import bcrypt

def parse_scraped_lecturers():
    """Parse lecturers from scraped_lecturers.txt"""
    lecturers = []
    
    try:
        with open('scraped_lecturers.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern: number. NAME ... | email@mmu.edu.my
        pattern = r'^\s*\d+\.\s+(.+?)\n.*?\|\s*([a-zA-Z0-9.@-]+@mmu\.edu\.my)'
        matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            name = match.group(1).strip()
            email = match.group(2).strip()
            
            # Clean up name (remove department titles)
            name = re.sub(r'\s+', ' ', name)  # Normalize whitespace
            
            if name and email:
                lecturers.append({
                    'name': name,
                    'email': email,
                    'department': 'FCI'  # All from scraped_lecturers.txt are FCI
                })
        
        return lecturers
    
    except FileNotFoundError:
        print("Warning: scraped_lecturers.txt not found, skipping lecturer seeding")
        return []

def init_production():
    """Initialize database for production - idempotent and safe"""
    
    with app.app_context():
        print("Production Database Initialization")
        print("=" * 60)
        
        # Create all tables if they don't exist
        try:
            db.create_all()
            print("OK - All tables created or verified")
        except Exception as e:
            print(f"Error creating tables: {e}")
            return False
        
        # Seed lecturers only if table is empty
        lecturer_count = Lecturer.query.count()
        if lecturer_count == 0:
            print("\nLoading lecturers from scraped_lecturers.txt...")
            lecturers = parse_scraped_lecturers()
            
            if lecturers:
                for i, lect_data in enumerate(lecturers, 1):
                    # Check if already exists
                    existing = Lecturer.query.filter_by(email=lect_data['email']).first()
                    if not existing:
                        lecturer = Lecturer(
                            name=lect_data['name'],
                            email=lect_data['email'],
                            department=lect_data['department']
                        )
                        db.session.add(lecturer)
                    
                    # Progress indicator
                    if i % 100 == 0:
                        print(f"  Loaded {i}/{len(lecturers)} lecturers...")
                
                db.session.commit()
                print(f"OK - Loaded {len(lecturers)} lecturers")
            else:
                print("Warning: No lecturers found in scraped_lecturers.txt")
        else:
            print(f"\nOK - Lecturer table already populated ({lecturer_count} lecturers)")
        
        # Create default admin accounts only if User table is empty
        user_count = User.query.count()
        if user_count == 0:
            print("\nCreating default admin accounts...")
            default_accounts = [
                ("owner@mmu.edu.my", "lecturer", "OWNER", "password123"),
                ("admin@mmu.edu.my", "lecturer", "ADMIN", "password123"),
                ("mod@mmu.edu.my", "lecturer", "MOD", "password123"),
            ]
            
            for email, user_type, role, password in default_accounts:
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
            print("OK - Default admin accounts created")
            print("\nDefault credentials (change in production):")
            print("  owner@mmu.edu.my : password123")
            print("  admin@mmu.edu.my : password123")
            print("  mod@mmu.edu.my : password123")
        else:
            print(f"\nOK - User table already populated ({user_count} users)")
        
        print("\n" + "=" * 60)
        print("Production initialization complete - all data preserved")
        return True

if __name__ == '__main__':
    init_production()
