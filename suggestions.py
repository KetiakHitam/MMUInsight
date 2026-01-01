from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_babel import gettext as _
from extensions import db
from models import Suggestion
from datetime import datetime
from sqlalchemy import desc

suggestions_bp = Blueprint('suggestions', __name__)

@suggestions_bp.route('/suggestions')
def suggestions_list():
    sort_by = request.args.get('sort', 'upvotes')
    
    if sort_by == 'newest':
        suggestions = Suggestion.query.order_by(desc(Suggestion.created_at)).all()
    else:  # default to upvotes
        suggestions = Suggestion.query.order_by(desc(Suggestion.upvotes)).all()
    
    return render_template('suggestions.html', suggestions=suggestions, sort_by=sort_by)

@suggestions_bp.route('/suggestions', methods=['POST'])
@login_required
def create_suggestion():
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    is_anonymous = request.form.get('is_anonymous') == 'on'
    
    if not title or not description:
        flash(_("Title and description are required"), "error")
        return redirect(url_for('suggestions.suggestions_list'))
    
    suggestion = Suggestion(
        user_id=None if is_anonymous else current_user.id,
        title=title,
        description=description,
        is_anonymous=is_anonymous
    )
    
    db.session.add(suggestion)
    db.session.commit()
    
    flash(_("Suggestion submitted successfully!"), "success")
    return redirect(url_for('suggestions.suggestions_list'))
