# search.py
from rapidfuzz import process, fuzz
from models import User


def search_lecturers_by_email(query, limit=20, threshold=60, prefilter_limit=500):
    """Return list of (User, score) sorted by descending score.

    To avoid scanning the whole table, first prefilter using a SQL ilike query limited to
    `prefilter_limit` rows. If no candidates are found, fall back to a bounded set of
    lecturers to keep response times reasonable.
    """
    if not query:
        return []

    # Prefilter with a case-insensitive SQL match to reduce the candidate set
    candidates = User.query.filter(
        User.user_type == 'lecturer',
        User.email.ilike(f"%{query}%")
    ).limit(prefilter_limit).all()

    # If no direct ilike matches were found, fall back to a bounded scan
    if not candidates:
        candidates = User.query.filter_by(user_type='lecturer').limit(prefilter_limit).all()

    emails = [u.email for u in candidates]
    # returns tuples (matched_string, score, index_in_input_list)
    matches = process.extract(query, emails, scorer=fuzz.WRatio, limit=limit)
    results = []
    for matched, score, idx in matches:
        if score >= threshold:
            results.append((candidates[idx], score))
    return results