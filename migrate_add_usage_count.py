"""
Migration to add usage_count column to Subject table
"""
from app import app
from extensions import db
from sqlalchemy import text

with app.app_context():
    try:
        # Try to add the column
        db.session.execute(text("ALTER TABLE subject ADD COLUMN usage_count INTEGER NOT NULL DEFAULT 0"))
        db.session.commit()
        print("✓ Successfully added usage_count column to subject table")
    except Exception as e:
        if "already exists" in str(e) or "duplicate column" in str(e):
            print("✓ Column already exists")
        else:
            print(f"✗ Error: {e}")
            db.session.rollback()
