from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from extensions import db
from models import StatusLog, Review, Lecturer
from sqlalchemy import func
import json

status_bp = Blueprint('status', __name__)

def get_uptime_percentage(days=30):
    """Calculate uptime percentage for the last N days"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Query errors in the period
    errors = StatusLog.query.filter(
        StatusLog.timestamp >= cutoff_date,
        StatusLog.status == 'error'
    ).all()
    
    if not errors:
        return 100.0
    
    # Simple calculation: if any error, consider that time as downtime
    # For a real system, you'd track actual downtime windows
    total_hours = days * 24
    downtime_hours = len(errors)  # Rough estimate
    uptime = max(0, 100 - (downtime_hours / total_hours * 100))
    return round(uptime, 2)

def get_system_status():
    """Determine overall system status from recent logs"""
    recent_errors = StatusLog.query.filter(
        StatusLog.timestamp >= datetime.utcnow() - timedelta(hours=24),
        StatusLog.status == 'error'
    ).all()
    
    if recent_errors:
        return 'degraded'
    
    recent_incidents = StatusLog.query.filter(
        StatusLog.timestamp >= datetime.utcnow() - timedelta(hours=24),
        StatusLog.event_type == 'incident'
    ).all()
    
    if recent_incidents:
        return 'warning'
    
    return 'operational'

@status_bp.route('/status', methods=['GET'])
def public_status():
    """Public-facing status page"""
    system_status = get_system_status()
    uptime_30d = get_uptime_percentage(30)
    
    # Get last update timestamp
    last_log = StatusLog.query.order_by(StatusLog.timestamp.desc()).first()
    last_updated = last_log.timestamp if last_log else datetime.utcnow()
    
    # Get recent incidents (unresolved only)
    recent_incidents = StatusLog.query.filter(
        StatusLog.event_type.in_(['incident', 'maintenance']),
        StatusLog.resolved_at.is_(None)
    ).order_by(StatusLog.timestamp.desc()).limit(5).all()
    
    # Get incident history (last 7 days, resolved)
    week_ago = datetime.utcnow() - timedelta(days=7)
    incident_history = StatusLog.query.filter(
        StatusLog.event_type.in_(['incident', 'maintenance']),
        StatusLog.resolved_at.isnot(None),
        StatusLog.timestamp >= week_ago
    ).order_by(StatusLog.timestamp.desc()).all()
    
    return render_template('status.html',
                         system_status=system_status,
                         uptime_30d=uptime_30d,
                         last_updated=last_updated,
                         recent_incidents=recent_incidents,
                         incident_history=incident_history)

@status_bp.route('/admin/status', methods=['GET'])
@login_required
def admin_status():
    """Admin-only status dashboard"""
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    from models import User, BugReport
    
    system_status = get_system_status()
    uptime_30d = get_uptime_percentage(30)
    
    # System metrics
    total_lecturers = Lecturer.query.count()
    total_reviews = Review.query.count()
    total_users = User.query.count()
    
    # Reviews this week
    week_ago = datetime.utcnow() - timedelta(days=7)
    reviews_this_week = Review.query.filter(
        Review.review_date >= week_ago
    ).count()
    
    # New users this week
    new_users_week = User.query.filter(
        User.created_at >= week_ago if hasattr(User, 'created_at') else True
    ).count() if hasattr(User, 'created_at') else 0
    
    # Flagged reviews waiting moderation
    flagged_reviews = Review.query.filter(
        Review.requires_human_review == True,
        Review.is_approved.is_(None)
    ).count()
    
    # Pending bug reports
    pending_bugs = BugReport.query.filter(
        BugReport.status.in_(['new', 'in_progress'])
    ).count()
    
    # Lecturers with bios
    lecturers_with_bios = Lecturer.query.filter(
        Lecturer.bio.isnot(None)
    ).count()
    bio_percentage = round((lecturers_with_bios / total_lecturers * 100), 1) if total_lecturers > 0 else 0
    
    # Claimed profiles
    claimed_profiles = Lecturer.query.filter(
        Lecturer.claimed_by_user_id.isnot(None)
    ).count()
    claimed_percentage = round((claimed_profiles / total_lecturers * 100), 1) if total_lecturers > 0 else 0
    
    # Profanity detections this week
    profanity_week = Review.query.filter(
        Review.review_date >= week_ago,
        Review.moderation_flags.like('%profanity%')
    ).count()
    
    # ASCII art detections this week
    ascii_week = Review.query.filter(
        Review.review_date >= week_ago,
        Review.moderation_flags.like('%ascii_art%')
    ).count()
    
    # Avg moderation time
    moderated_reviews = Review.query.filter(
        Review.moderated_at.isnot(None),
        Review.review_date.isnot(None)
    ).all()
    
    avg_moderation_hours = 0
    if moderated_reviews:
        total_time = sum([
            (r.moderated_at - r.review_date).total_seconds()
            for r in moderated_reviews
        ])
        avg_moderation_hours = round(total_time / len(moderated_reviews) / 3600, 1)
    
    # Last scraper run
    last_scraper_run = StatusLog.query.filter(
        StatusLog.event_type == 'scraper_run'
    ).order_by(StatusLog.timestamp.desc()).first()
    
    scraper_status = None
    if last_scraper_run:
        scraper_status = {
            'timestamp': last_scraper_run.timestamp,
            'status': last_scraper_run.status,
            'title': last_scraper_run.title
        }
        if last_scraper_run.details:
            try:
                scraper_status['details'] = json.loads(last_scraper_run.details)
            except:
                pass
    
    # Recent logs (last 20)
    recent_logs = StatusLog.query.order_by(
        StatusLog.timestamp.desc()
    ).limit(20).all()
    
    # Error logs (last 24 hours)
    error_logs = StatusLog.query.filter(
        StatusLog.status == 'error',
        StatusLog.timestamp >= datetime.utcnow() - timedelta(hours=24)
    ).order_by(StatusLog.timestamp.desc()).all()
    
    return render_template('admin_status.html',
                         system_status=system_status,
                         uptime_30d=uptime_30d,
                         total_lecturers=total_lecturers,
                         total_reviews=total_reviews,
                         total_users=total_users,
                         reviews_this_week=reviews_this_week,
                         new_users_week=new_users_week,
                         flagged_reviews=flagged_reviews,
                         pending_bugs=pending_bugs,
                         bio_percentage=bio_percentage,
                         claimed_percentage=claimed_percentage,
                         profanity_week=profanity_week,
                         ascii_week=ascii_week,
                         avg_moderation_hours=avg_moderation_hours,
                         scraper_status=scraper_status,
                         recent_logs=recent_logs,
                         error_logs=error_logs)

def log_status_event(event_type, title, status='info', description=None, details=None):
    """Helper function to log system events"""
    log_entry = StatusLog(
        event_type=event_type,
        title=title,
        status=status,
        description=description,
        details=json.dumps(details) if details else None
    )
    db.session.add(log_entry)
    db.session.commit()
    return log_entry

def resolve_incident(log_id, resolution_notes=None):
    """Mark an incident as resolved"""
    log_entry = StatusLog.query.get(log_id)
    if log_entry:
        log_entry.resolved_at = datetime.utcnow()
        if resolution_notes:
            log_entry.description = resolution_notes
        db.session.commit()
    return log_entry
