"""
Quick migration script to add moderation columns to review table
"""

import sqlite3
import os

def migrate_database():
    """Add moderation columns to review table"""
    
    # Find the database file
    db_paths = [
        'database/mmuinsight.db',
        'instance/lecturers.db',
        'lecturers.db',
        'database.db',
        'app.db'
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("✗ Could not find database file")
        print("  Checked:", ', '.join(db_paths))
        print("\n  Try this instead:")
        print("  1. Delete your database file")
        print("  2. Restart Flask app to recreate it")
        return False
    
    print(f"Found database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # SQL commands to add missing columns
        columns = [
            ('moderation_flags', 'TEXT'),
            ('moderation_severity', 'VARCHAR(20)'),
            ('requires_human_review', 'BOOLEAN'),
            ('is_approved', 'BOOLEAN')
        ]
        
        for col_name, col_type in columns:
            try:
                cursor.execute(f'ALTER TABLE review ADD COLUMN {col_name} {col_type}')
                print(f"✓ Added column: {col_name}")
            except sqlite3.OperationalError as e:
                if "already exists" in str(e):
                    print(f"✓ Column already exists: {col_name}")
                else:
                    raise
        
        conn.commit()
        conn.close()
        
        print("\n✓ Database migration successful!")
        print("✓ You can now refresh your app")
        return True
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        return False

if __name__ == '__main__':
    migrate_database()
