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
    verification_token = db.Column(db.String(100), nullable=True)
    verification_token_created_at = db.Column(db.DateTime, nullable=True)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_created_at = db.Column(db.DateTime, nullable=True)
    bio = db.Column(db.Text, nullable=True)
    last_online = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    dark_mode = db.Column(db.Boolean, nullable=False, default=False)

    reviews_written = db.relationship('Review', foreign_keys='Review.user_id', backref='author', lazy=True)
    reviews_received = db.relationship('Review', foreign_keys='Review.lecturer_id', backref='lecturer', lazy=True)
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

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_code = db.Column(db.String(100), nullable=True)
    subject_name = db.Column(db.String(100), nullable=False)

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
    lecturer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=True)
    review_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_anonymous = db.Column(db.Boolean, nullable=False, default=False)
    is_pinned = db.Column(db.Boolean, nullable=False, default=False)
    subject_code = db.Column(db.String(100), nullable=True)
    
    replies = db.relationship('Reply', backref='review', lazy=True, cascade='all, delete-orphan')
    reports = db.relationship('Report', backref='review', lazy=True)

class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reply_text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey('review.id'), nullable=False)
    reply_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_edited = db.Column(db.Boolean, nullable=False, default=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

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
