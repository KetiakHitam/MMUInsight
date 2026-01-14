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

def search_lecturers_by_email(query):
    if not query:
        return []

    lecturers = User.query.filter(
        User.user_type == 'lecturer',
        or_(User.role.is_(None), User.role == "", User.role.notin_(["OWNER", "ADMIN", "MOD"])),
        User.email.ilike(f"%{query}%")
    ).all()

    lecturer_ids = [l.id for l in lecturers]
    if not lecturer_ids:
        return lecturers

    stats_rows = (
        db.session.query(
            Review.lecturer_id,
            func.count(Review.id).label("review_count"),
            func.avg(
                (
                    Review.rating_clarity
                    + Review.rating_engagement
                    + Review.rating_punctuality
                    + Review.rating_responsiveness
                    + Review.rating_fairness
                )
                / 5.0
            ).label("avg_rating"),
        )
        .filter(Review.lecturer_id.in_(lecturer_ids))
        .group_by(Review.lecturer_id)
        .all()
    )
    stats_by_id = {
        row.lecturer_id: {
            "review_count": int(row.review_count or 0),
            "avg_rating": float(row.avg_rating) if row.avg_rating is not None else None,
        }
        for row in stats_rows
    }

    subject_rows = (
        db.session.query(
            Review.lecturer_id,
            Review.subject_code,
            func.count(Review.id).label("subject_count"),
        )
        .filter(
            Review.lecturer_id.in_(lecturer_ids),
            Review.subject_code.isnot(None),
            Review.subject_code != "",
        )
        .group_by(Review.lecturer_id, Review.subject_code)
        .all()
    )

    top_subject_by_id = {}
    for row in subject_rows:
        current = top_subject_by_id.get(row.lecturer_id)
        if current is None or int(row.subject_count) > current[1]:
            top_subject_by_id[row.lecturer_id] = (row.subject_code, int(row.subject_count))

    for lecturer in lecturers:
        stats = stats_by_id.get(lecturer.id, {})
        lecturer.review_count = stats.get("review_count", 0)
        avg = stats.get("avg_rating")
        lecturer.avg_rating = round(avg, 1) if avg is not None else None
        lecturer.top_subject_code = (top_subject_by_id.get(lecturer.id) or (None, 0))[0]
        lecturer.avatar_initials = _email_initials(lecturer.email)

    return lecturers