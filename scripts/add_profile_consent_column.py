"""
Small helper to add the 'profile_consent' column to the 'user' table if it doesn't exist.
Run from project root with the venv activated:

    python scripts/add_profile_consent_column.py

This will ALTER TABLE only if needed (SQLite).
"""
import sqlite3
import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'database', 'mmuinsight.db')

if not os.path.exists(DB_PATH):
    print("Database not found at", DB_PATH)
    raise SystemExit(1)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("PRAGMA table_info('user')")
columns = [row[1] for row in cur.fetchall()]
if 'profile_consent' in columns:
    print("Column 'profile_consent' already exists. Nothing to do.")
else:
    print("Adding 'profile_consent' column to 'user' table...")
    cur.execute("ALTER TABLE user ADD COLUMN profile_consent INTEGER NOT NULL DEFAULT 0;")
    conn.commit()
    print("Done.")

conn.close()
