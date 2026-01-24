import sqlite3
from datetime import datetime

def add_moderation_history_columns():
    """Add moderation history tracking columns to review table"""
    db_path = 'database/mmuinsight.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    columns_to_add = [
        ('moderated_by_id', 'INTEGER'),
        ('moderated_at', 'DATETIME'),
        ('moderation_action', 'VARCHAR(20)')  # 'approved' or 'rejected'
    ]
    
    for column_name, column_type in columns_to_add:
        try:
            cursor.execute(f'ALTER TABLE review ADD COLUMN {column_name} {column_type}')
            print(f"✓ Added column: {column_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"⚠ Column {column_name} already exists")
            else:
                print(f"✗ Error adding {column_name}: {e}")
    
    conn.commit()
    conn.close()
    print("\n✓ Migration completed successfully!")

if __name__ == '__main__':
    add_moderation_history_columns()
