from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_babel import gettext as _
from auth.decorators import admin_required
from extensions import db
from models import Changelog
from audit import log_admin_action
from datetime import datetime
from sqlalchemy import desc

changelog_bp = Blueprint('changelog', __name__)

@changelog_bp.route('/changelog')
def changelog_list():
    """Public changelog view - shows published entries only"""
    entries = Changelog.query.filter_by(is_published=True).order_by(desc(Changelog.created_at)).all()
    return render_template('changelog.html', entries=entries, now=datetime.utcnow())

@changelog_bp.route('/admin/changelog')
@admin_required
def admin_changelog():
    """Admin changelog management view - shows all entries"""
    entries = Changelog.query.order_by(desc(Changelog.created_at)).all()
    return render_template('admin_changelog.html', entries=entries, now=datetime.utcnow())

@changelog_bp.route('/admin/changelog/create', methods=['GET', 'POST'])
@admin_required
def create_changelog_entry():
    """Create a new changelog entry"""
    if request.method == 'GET':
        return render_template('create_changelog_entry.html')
    
    version = request.form.get('version', '').strip()
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    is_published = request.form.get('is_published') == 'on'
    
    if not version or not title or not content:
        flash(_("Version, title, and content are required"), "error")
        return redirect(url_for('changelog.create_changelog_entry'))
    
    # Check if version already exists
    if Changelog.query.filter_by(version=version).first():
        flash(_("Version already exists"), "error")
        return redirect(url_for('changelog.create_changelog_entry'))
    
    changelog = Changelog(
        version=version,
        title=title,
        content=content,
        user_id=current_user.id,
        is_published=is_published
    )
    
    db.session.add(changelog)
    db.session.commit()
    
    log_admin_action(f"Created changelog entry version {version}", "changelog")
    flash(_("Changelog entry created successfully!"), "success")
    return redirect(url_for('changelog.admin_changelog'))

@changelog_bp.route('/admin/changelog/<int:entry_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_changelog_entry(entry_id):
    """Edit an existing changelog entry"""
    entry = Changelog.query.get_or_404(entry_id)
    
    if request.method == 'GET':
        return render_template('edit_changelog_entry.html', entry=entry)
    
    version = request.form.get('version', '').strip()
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    is_published = request.form.get('is_published') == 'on'
    
    if not version or not title or not content:
        flash(_("Version, title, and content are required"), "error")
        return redirect(url_for('changelog.edit_changelog_entry', entry_id=entry_id))
    
    # Check if new version is different and already exists
    if version != entry.version and Changelog.query.filter_by(version=version).first():
        flash(_("Version already exists"), "error")
        return redirect(url_for('changelog.edit_changelog_entry', entry_id=entry_id))
    
    old_version = entry.version
    entry.version = version
    entry.title = title
    entry.content = content
    entry.is_published = is_published
    entry.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    log_admin_action(f"Updated changelog entry {old_version} -> {version}", "changelog")
    flash(_("Changelog entry updated successfully!"), "success")
    return redirect(url_for('changelog.admin_changelog'))

@changelog_bp.route('/admin/changelog/<int:entry_id>/delete', methods=['POST'])
@admin_required
def delete_changelog_entry(entry_id):
    """Delete a changelog entry"""
    entry = Changelog.query.get_or_404(entry_id)
    version = entry.version
    
    db.session.delete(entry)
    db.session.commit()
    
    log_admin_action(f"Deleted changelog entry version {version}", "changelog")
    flash(_("Changelog entry deleted successfully!"), "success")
    return redirect(url_for('changelog.admin_changelog'))

@changelog_bp.route('/admin/changelog/<int:entry_id>/toggle-publish', methods=['POST'])
@admin_required
def toggle_publish_changelog_entry(entry_id):
    """Toggle publish status of a changelog entry"""
    entry = Changelog.query.get_or_404(entry_id)
    
    entry.is_published = not entry.is_published
    db.session.commit()
    
    status = "published" if entry.is_published else "unpublished"
    log_admin_action(f"Toggled changelog entry {entry.version} to {status}", "changelog")
    flash(_("Changelog entry published status updated!"), "success")
    return redirect(url_for('changelog.admin_changelog'))
