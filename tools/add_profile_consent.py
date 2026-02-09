import os
import sqlite3


def get_db_path() -> str:
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'mmuinsight.db')


def table_exists(cursor, table: str) -> bool:
    cursor.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1",
        (table,),
    )
    return cursor.fetchone() is not None


def get_columns(cursor, table: str) -> set[str]:
    cursor.execute(f"PRAGMA table_info('{table}')")
    return {row[1] for row in cursor.fetchall()}


def add_column_if_missing(cursor, table: str, name: str, ddl: str) -> bool:
    if not table_exists(cursor, table):
        print(f"Table '{table}' not found; skipping {table}.{name}")
        return False

    cols = get_columns(cursor, table)
    if name in cols:
        print(f"{table}.{name} already present")
        return False

    try:
        cursor.execute(ddl)
        print(f"Added {table}.{name}")
        return True
    except Exception as e:
        print(f"Failed to add {table}.{name}:", e)
        return False


db = get_db_path()
if not os.path.exists(db):
    print('DB not found:', db)
    raise SystemExit(1)

conn = sqlite3.connect(db)
try:
    c = conn.cursor()
    if table_exists(c, 'user'):
        print('user columns before:', sorted(get_columns(c, 'user')))

    changed = False

    # Added over time in User model
    changed |= add_column_if_missing(c, 'user', 'profile_consent', "ALTER TABLE user ADD COLUMN profile_consent INTEGER NOT NULL DEFAULT 0")
    changed |= add_column_if_missing(c, 'user', 'search_history', "ALTER TABLE user ADD COLUMN search_history TEXT NULL")
    changed |= add_column_if_missing(c, 'user', 'password_is_temporary', "ALTER TABLE user ADD COLUMN password_is_temporary INTEGER NOT NULL DEFAULT 0")
    changed |= add_column_if_missing(c, 'user', 'dark_mode', "ALTER TABLE user ADD COLUMN dark_mode INTEGER NOT NULL DEFAULT 0")
    changed |= add_column_if_missing(c, 'user', 'total_upvotes', "ALTER TABLE user ADD COLUMN total_upvotes INTEGER NOT NULL DEFAULT 0")
    changed |= add_column_if_missing(c, 'user', 'reliable_tag', "ALTER TABLE user ADD COLUMN reliable_tag INTEGER NOT NULL DEFAULT 0")

    # Review moderation / ASCII detector additions
    changed |= add_column_if_missing(c, 'review', 'upvotes', "ALTER TABLE review ADD COLUMN upvotes INTEGER NOT NULL DEFAULT 0")
    changed |= add_column_if_missing(c, 'review', 'downvotes', "ALTER TABLE review ADD COLUMN downvotes INTEGER NOT NULL DEFAULT 0")
    changed |= add_column_if_missing(c, 'review', 'moderation_flags', "ALTER TABLE review ADD COLUMN moderation_flags TEXT NULL")
    changed |= add_column_if_missing(c, 'review', 'moderation_severity', "ALTER TABLE review ADD COLUMN moderation_severity VARCHAR(20) NULL")
    changed |= add_column_if_missing(c, 'review', 'requires_human_review', "ALTER TABLE review ADD COLUMN requires_human_review INTEGER NOT NULL DEFAULT 0")
    changed |= add_column_if_missing(c, 'review', 'is_approved', "ALTER TABLE review ADD COLUMN is_approved INTEGER NULL")
    changed |= add_column_if_missing(c, 'review', 'moderated_by_id', "ALTER TABLE review ADD COLUMN moderated_by_id INTEGER NULL")
    changed |= add_column_if_missing(c, 'review', 'moderated_at', "ALTER TABLE review ADD COLUMN moderated_at DATETIME NULL")
    changed |= add_column_if_missing(c, 'review', 'moderation_action', "ALTER TABLE review ADD COLUMN moderation_action VARCHAR(20) NULL")
    changed |= add_column_if_missing(c, 'review', 'ascii_art_score', "ALTER TABLE review ADD COLUMN ascii_art_score INTEGER NOT NULL DEFAULT 0")

    # Suggestion / Bug reports ASCII detector additions
    changed |= add_column_if_missing(c, 'suggestion', 'ascii_art_score', "ALTER TABLE suggestion ADD COLUMN ascii_art_score INTEGER NOT NULL DEFAULT 0")
    changed |= add_column_if_missing(c, 'bug_report', 'ascii_art_score', "ALTER TABLE bug_report ADD COLUMN ascii_art_score INTEGER NOT NULL DEFAULT 0")

    if changed:
        conn.commit()

    if table_exists(c, 'user'):
        print('user columns after:', sorted(get_columns(c, 'user')))
    if table_exists(c, 'review'):
        print('review columns after:', sorted(get_columns(c, 'review')))
    if table_exists(c, 'suggestion'):
        print('suggestion columns after:', sorted(get_columns(c, 'suggestion')))
    if table_exists(c, 'bug_report'):
        print('bug_report columns after:', sorted(get_columns(c, 'bug_report')))
finally:
    conn.close()
