from flask_login import UserMixin
from extensions import db
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    user_type = db.Column(db.String(10), nullable=False, default='student')
    role = db.Column(db.String(10), nullable=True)
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    is_claimed = db.Column(db.Boolean, nullable=False, default=False)
    # Whether the student has accepted the site-wide lecturer-profile consent notice
    profile_consent = db.Column(db.Boolean, nullable=False, default=False)
    verification_token = db.Column(db.String(100), nullable=True)
    verification_token_created_at = db.Column(db.DateTime, nullable=True)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_created_at = db.Column(db.DateTime, nullable=True)
    bio = db.Column(db.Text, nullable=True)
    last_online = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    dark_mode = db.Column(db.Boolean, nullable=False, default=False)
    search_history = db.Column(db.Text, nullable=True)
    # Total upvotes across all reviews authored by this user (kept in sync by vote handlers)
    total_upvotes = db.Column(db.Integer, nullable=False, default=0)
    # Persistent reliable tag: 1 when the user reached threshold, never unset by app logic
    reliable_tag = db.Column(db.Integer, nullable=False, default=0)

    reviews_written = db.relationship('Review', foreign_keys='Review.user_id', backref='author', lazy=True)
    replies = db.relationship('Reply', backref='author', lazy=True)
    reports_made = db.relationship('Report', backref='reporter', lazy=True)
    
    def is_owner(self):
        return self.role == 'OWNER'
    
    def is_admin(self):
        return self.role in ['OWNER', 'ADMIN']
    
    def is_mod(self):
        return self.role in ['OWNER', 'ADMIN', 'MOD']
    
    def can_manage_user(self, target_user):
        if self.is_owner():
            return True
        if self.is_admin():
            return target_user.role not in ['OWNER', 'ADMIN']
        return False
    
    def can_change_role(self, target_user, new_role):
        if self.is_owner():
            return new_role in ['OWNER', 'ADMIN', 'MOD']
        if self.is_admin():
            return new_role in ['MOD'] and target_user.role not in ['OWNER', 'ADMIN']
        return False
    
    def can_delete_user(self, target_user):
        if target_user.is_owner():
            return False
        if target_user.is_admin() and not self.is_owner():
            return False
        return self.is_mod()
    
    def can_suspend_user(self, target_user):
        if target_user.is_owner():
            return False
        if target_user.is_admin() and not self.is_owner():
            return False
        return self.is_mod()

class Lecturer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    department = db.Column(db.String(100), nullable=True)
    claimed_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    reviews = db.relationship('Review', backref='lecturer', lazy=True, cascade='all, delete-orphan')
    claimed_by_user = db.relationship('User', backref='claimed_lecturer_profiles', lazy=True)
    
    def is_verified(self):
        """Check if this lecturer has claimed their profile"""
        return self.claimed_by_user_id is not None

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_code = db.Column(db.String(100), nullable=True)
    subject_name = db.Column(db.String(100), nullable=False)
    usage_count = db.Column(db.Integer, nullable=False, default=0)

    reviews = db.relationship('Review', backref='subject', lazy=True)

class Review(db.Model):
    @property
    def overall_score(self):
        ratings = [
            self.rating_clarity,
            self.rating_engagement,
            self.rating_punctuality,
            self.rating_responsiveness,
            self.rating_fairness
        ]
        return round(sum(ratings) / len(ratings), 1)
    id = db.Column(db.Integer, primary_key=True)
    review_text = db.Column(db.Text, nullable=False)
    rating_clarity = db.Column(db.Integer, nullable=False)
    rating_engagement = db.Column(db.Integer, nullable=False)
    rating_punctuality = db.Column(db.Integer, nullable=False)
    rating_responsiveness = db.Column(db.Integer, nullable=False)
    rating_fairness = db.Column(db.Integer, nullable=False)
    recommend = db.Column(db.Boolean, nullable=False, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturer.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=True)
    review_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_anonymous = db.Column(db.Boolean, nullable=False, default=False)
    is_pinned = db.Column(db.Boolean, nullable=False, default=False)
    subject_code = db.Column(db.String(100), nullable=True)
    upvotes = db.Column(db.Integer, nullable=False, default=0)
    downvotes = db.Column(db.Integer, nullable=False, default=0)
    moderation_flags = db.Column(db.Text, nullable=True) 
    moderation_severity = db.Column(db.String(20), nullable=True)  
    requires_human_review = db.Column(db.Boolean, nullable=False, default=False)
    is_approved = db.Column(db.Boolean, nullable=True)  
    moderated_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    moderated_at = db.Column(db.DateTime, nullable=True)
    moderation_action = db.Column(db.String(20), nullable=True)
    ascii_art_score = db.Column(db.Integer, nullable=False, default=0)
    
    replies = db.relationship('Reply', backref='review', lazy=True, cascade='all, delete-orphan')
    reports = db.relationship('Report', backref='review', lazy=True)
    moderated_by = db.relationship('User', foreign_keys=[moderated_by_id], backref='moderated_reviews')

class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reply_text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey('review.id'), nullable=False)
    reply_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_edited = db.Column(db.Boolean, nullable=False, default=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    upvotes = db.Column(db.Integer, nullable=False, default=0)
    downvotes = db.Column(db.Integer, nullable=False, default=0)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey('review.id'), nullable=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    report_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Suggestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    is_anonymous = db.Column(db.Boolean, nullable=False, default=False)
    upvotes = db.Column(db.Integer, nullable=False, default=0)
    downvotes = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(20), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ascii_art_score = db.Column(db.Integer, nullable=False, default=0)
    
    user = db.relationship('User', backref='suggestions', lazy=True)
    votes = db.relationship('SuggestionVote', backref='suggestion', lazy=True, cascade='all, delete-orphan')

class SuggestionVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    suggestion_id = db.Column(db.Integer, db.ForeignKey('suggestion.id'), nullable=False)
    vote_type = db.Column(db.String(10), nullable=False)  # 'upvote' or 'downvote'
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    role = db.Column(db.String(10), nullable=True)
    action = db.Column(db.String(255), nullable=False)
    target_type = db.Column(db.String(50), nullable=False)

    user = db.relationship('User', backref='audit_logs', lazy=True)

class ReviewVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey('review.id'), nullable=False)
    vote_type = db.Column(db.String(10), nullable=False)  # 'upvote' or 'downvote'
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', backref='review_votes', lazy=True)
    review = db.relationship('Review', backref='votes', lazy=True)

class ReplyVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reply_id = db.Column(db.Integer, db.ForeignKey('reply.id'), nullable=False)
    vote_type = db.Column(db.String(10), nullable=False)  # 'upvote' or 'downvote'
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', backref='reply_votes', lazy=True)
    reply = db.relationship('Reply', backref='votes', lazy=True)

class BugReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='new')  # new, in_progress, resolved, closed
    priority = db.Column(db.String(20), nullable=False, default='normal')  # low, normal, high, critical
    reported_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    internal_notes = db.Column(db.Text, nullable=True)
    resolution_notes = db.Column(db.Text, nullable=True)
    ascii_art_score = db.Column(db.Integer, nullable=False, default=0)
    
    user = db.relationship('User', backref='bug_reports', lazy=True)
    comments = db.relationship('BugComment', backref='bug_report', lazy=True, cascade='all, delete-orphan')

class BugComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bug_report_id = db.Column(db.Integer, db.ForeignKey('bug_report.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    user = db.relationship('User', backref='bug_comments', lazy=True)
