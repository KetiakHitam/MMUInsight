from __future__ import annotations

from sqlalchemy.exc import OperationalError
from flask_login import current_user

from extensions import db
from models import AuditLog


def _ensure_audit_table_exists() -> None:
    """Create the audit_log table if it doesn't exist yet."""
    try:
        AuditLog.__table__.create(db.engine, checkfirst=True)
    except Exception:
        pass


def log_action(action: str, target_type: str, *, user_id: int | None = None, role: str | None = None) -> None:
    """Write an audit log entry.

    Safe to call from any request context (including anonymous routes).
    This should never raise in normal request flow.
    """
    try:
        _ensure_audit_table_exists()

        if user_id is None:
            return

        entry = AuditLog(
            user_id=user_id,
            role=role,
            action=action,
            target_type=target_type,
        )
        db.session.add(entry)
        db.session.commit()
    except OperationalError:
        try:
            db.session.rollback()
        except Exception:
            pass
    except Exception:
        try:
            db.session.rollback()
        except Exception:
            pass


def log_admin_action(action: str, target_type: str) -> None:
    """Write an audit log entry for the current admin/mod action.

    This should never raise in normal request flow.
    """
    user_id = getattr(current_user, "id", None)
    role = getattr(current_user, "role", None)
    log_action(action, target_type, user_id=user_id, role=role)
