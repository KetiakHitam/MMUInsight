"""
Blueprint: email search integrated with this repository.

Place this file at: routes/search.py

This code uses the project's existing db and User model:
- db is provided by extensions.py (Flask-SQLAlchemy)
- User is defined in models.py

It renders templates/index.html (search form) and templates/results.html (search results).
"""
from flask import Blueprint, request, render_template, redirect, url_for
from flask_login import login_required
from extensions import db
from models import User

search_bp = Blueprint("search", __name__, template_folder="../templates")


def _search_emails(session, q: str, limit: int = 200):
    """
    Simple, safe case-insensitive substring search on User.email.
    - session: db.session (Flask-SQLAlchemy)
    - q: raw user query (already stripped by caller)
    - limit: maximum number of rows returned
    Returns: (results_list, total_count)
    """
    if not q:
        return [], 0

    pattern = f"%{q}%"
    # Use SQLAlchemy's ilike for case-insensitive search; SQLAlchemy handles parameterization
    query = session.query(User).filter(User.email.ilike(pattern))
    total = query.count()
    results = query.order_by(User.email).limit(limit).all()
    return results, total


@search_bp.route("/", methods=["GET"])
def index():
    """
    Render the index page which includes the search bar.
    GET /  -> shows the form
    Submitting the form issues GET /search?q=...
    """
    return render_template("index.html")


@search_bp.route("/search", methods=["GET"])
@login_required
def search_results():
    """
    Handle GET /search?q=... and render results.html with matches.
    The route is protected with @login_required so only authenticated users can view actual emails.
    """
    q = (request.args.get("q") or "").strip()
    if not q:
        # If no query provided, redirect back to the index page
        return redirect(url_for("search.index"))

    page = 1
    per_page = 200  # you can expose pagination to the UI later if needed

    results_list, total = _search_emails(db.session, q=q, limit=per_page)
    emails = [u.email for u in results_list]

    return render_template("results.html", q=q, emails=emails, total=total)