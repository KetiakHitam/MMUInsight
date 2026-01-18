from rapidfuzz import process, fuzz
from sqlalchemy import func
from sqlalchemy import or_

from extensions import db
from models import User, Review


def _email_initials(email: str) -> str:
    if not email:
        return "?"
    local_part = email.split("@", 1)[0]
    parts = [p for p in local_part.replace("_", ".").split(".") if p]
    if len(parts) >= 2:
        return (parts[0][:1] + parts[1][:1]).upper()
    return local_part[:2].upper()

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