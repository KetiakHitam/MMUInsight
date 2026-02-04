import sqlite3, os
db = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'mmuinsight.db')
if not os.path.exists(db):
    print('DB not found:', db)
    raise SystemExit(1)
conn = sqlite3.connect(db)
c = conn.cursor()
c.execute("PRAGMA table_info('user')")
cols = [r[1] for r in c.fetchall()]
print('columns before:', cols)
if 'profile_consent' not in cols:
    try:
        c.execute("ALTER TABLE user ADD COLUMN profile_consent INTEGER NOT NULL DEFAULT 0")
        conn.commit()
        print('Added profile_consent column')
    except Exception as e:
        print('Failed to add profile_consent column:', e)
else:
    print('profile_consent already present')

if 'search_history' not in cols:
    try:
        c.execute("ALTER TABLE user ADD COLUMN search_history TEXT NULL")
        conn.commit()
        print('Added search_history column')
    except Exception as e:
        print('Failed to add search_history column:', e)
else:
    print('search_history already present')
conn.close()
