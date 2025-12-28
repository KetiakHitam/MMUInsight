# search.py
from rapidfuzz import process, fuzz
from models import User

def search_lecturers_by_email(query, limit=20, threshold=60):
    """Return list of (User, score) sorted by descending score."""
    if not query:
        return []
    lecturers = User.query.filter_by(user_type='lecturer').all()
    emails = [u.email for u in lecturers]
    # returns tuples (matched_string, score, index_in_input_list)
    matches = process.extract(query, emails, scorer=fuzz.WRatio, limit=limit)
    results = []
    for matched, score, idx in matches:
        if score >= threshold:
            results.append((lecturers[idx], score))
    return results