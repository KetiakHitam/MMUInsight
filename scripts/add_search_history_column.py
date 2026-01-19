import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from sqlalchemy import text

def add_search_history_column():
    with app.app_context():
        with db.engine.connect() as conn:
            try:
                conn.execute(text("ALTER TABLE user ADD COLUMN search_history TEXT"))
                print("Added search_history column to user table")
            except Exception as e:
                print(f"Error adding column (might already exist): {e}")

if __name__ == "__main__":
    add_search_history_column()
