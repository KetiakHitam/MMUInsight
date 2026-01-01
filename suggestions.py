from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_babel import gettext as _
from extensions import db
from models import Suggestion, SuggestionVote
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
    
    return render_template('suggestions.html', suggestions=suggestions, sort_by=sort_by, now=datetime.utcnow())

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

@suggestions_bp.route('/suggestion/<int:suggestion_id>/upvote', methods=['POST'])
@login_required
def upvote_suggestion(suggestion_id):
    suggestion = Suggestion.query.get_or_404(suggestion_id)
    
    existing_vote = SuggestionVote.query.filter_by(
        user_id=current_user.id,
        suggestion_id=suggestion_id
    ).first()
    
    if existing_vote:
        if existing_vote.vote_type == 'upvote':
            db.session.delete(existing_vote)
            suggestion.upvotes -= 1
        else:
            existing_vote.vote_type = 'upvote'
            suggestion.downvotes -= 1
            suggestion.upvotes += 1
    else:
        vote = SuggestionVote(
            user_id=current_user.id,
            suggestion_id=suggestion_id,
            vote_type='upvote'
        )
        db.session.add(vote)
        suggestion.upvotes += 1
    
    db.session.commit()
    return redirect(url_for('suggestions.suggestions_list'))

@suggestions_bp.route('/suggestion/<int:suggestion_id>/downvote', methods=['POST'])
@login_required
def downvote_suggestion(suggestion_id):
    suggestion = Suggestion.query.get_or_404(suggestion_id)
    
    existing_vote = SuggestionVote.query.filter_by(
        user_id=current_user.id,
        suggestion_id=suggestion_id
    ).first()
    
    if existing_vote:
        if existing_vote.vote_type == 'downvote':
            db.session.delete(existing_vote)
            suggestion.downvotes -= 1
        else:
            existing_vote.vote_type = 'downvote'
            suggestion.upvotes -= 1
            suggestion.downvotes += 1
    else:
        vote = SuggestionVote(
            user_id=current_user.id,
            suggestion_id=suggestion_id,
            vote_type='downvote'
        )
        db.session.add(vote)
        suggestion.downvotes += 1
    
    db.session.commit()
    return redirect(url_for('suggestions.suggestions_list'))
