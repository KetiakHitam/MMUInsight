# search.py
from models import User

def search_lecturers_by_email(query):
    if not query:
        return []
    return User.query.filter(
        User.user_type == 'lecturer',
        User.email.ilike(f"%{query}%")
    ).all()