# -*- coding: utf-8 -*-
import json
import secrets
from datetime import datetime
from functools import wraps

from flask import g, jsonify, request, session
from sqlalchemy.exc import OperationalError
from werkzeug.security import check_password_hash, generate_password_hash

from . import db
from .models import AdminAuditLog, AdminUser, MediaAsset

ADMIN_SESSION_KEY = "ensure_admin_user_id"
ADMIN_USERNAME_KEY = "ensure_admin_username"
ADMIN_ROLE_KEY = "ensure_admin_role"
ADMIN_CSRF_KEY = "ensure_admin_csrf"


def ensure_admin_tables():
    for table in (AdminUser.__table__, AdminAuditLog.__table__, MediaAsset.__table__):
        try:
            table.create(bind=db.engine, checkfirst=True)
        except OperationalError as exc:
            if "already exists" not in str(exc).lower():
                raise


def _json_text(value):
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False, default=str)


def serialize_admin_user(user: AdminUser | None):
    if not user:
        return None
    return {
        "id": int(user.id),
        "username": str(user.username),
        "role": str(user.role or "admin"),
        "is_active": bool(user.is_active),
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
    }


def current_admin():
    user_id = session.get(ADMIN_SESSION_KEY)
    if not user_id:
        return None
    user = db.session.get(AdminUser, int(user_id))
    if not user or not user.is_active:
        session.clear()
        return None
    g.admin_user = user
    return user


def get_csrf_token():
    token = session.get(ADMIN_CSRF_KEY)
    if token:
        return token
    token = secrets.token_urlsafe(32)
    session[ADMIN_CSRF_KEY] = token
    return token


def login_admin_session(user: AdminUser):
    session.clear()
    session.permanent = True
    session[ADMIN_SESSION_KEY] = int(user.id)
    session[ADMIN_USERNAME_KEY] = str(user.username)
    session[ADMIN_ROLE_KEY] = str(user.role or "admin")
    return get_csrf_token()


def logout_admin_session():
    session.clear()


def verify_admin_credentials(username: str, password: str):
    name = str(username or "").strip()
    raw_password = str(password or "")
    if not name or not raw_password:
        return None
    user = AdminUser.query.filter_by(username=name).first()
    if not user or not user.is_active:
        return None
    if not check_password_hash(user.password_hash, raw_password):
        return None
    user.last_login_at = datetime.utcnow()
    db.session.add(user)
    db.session.commit()
    return user


def upsert_admin_user(username: str, password: str, role: str = "admin", is_active: bool = True):
    name = str(username or "").strip()
    raw_password = str(password or "")
    if not name:
        raise ValueError("username is required")
    if not raw_password:
        raise ValueError("password is required")

    password_hash = generate_password_hash(raw_password, method="scrypt")
    user = AdminUser.query.filter_by(username=name).first()
    created = False
    if not user:
        user = AdminUser(username=name)
        created = True
    user.password_hash = password_hash
    user.role = role or "admin"
    user.is_active = bool(is_active)
    db.session.add(user)
    db.session.commit()
    return user, created


def audit_admin_action(action: str, table_name: str = "", record_pk: str = "", before=None, after=None, user=None):
    actor = user or getattr(g, "admin_user", None)
    log = AdminAuditLog(
        user_id=int(actor.id) if actor else None,
        username=str(actor.username) if actor else str(session.get(ADMIN_USERNAME_KEY) or ""),
        role=str(actor.role) if actor else str(session.get(ADMIN_ROLE_KEY) or ""),
        action=str(action or ""),
        table_name=str(table_name or ""),
        record_pk=str(record_pk or ""),
        before_json=_json_text(before),
        after_json=_json_text(after),
        ip_address=str(request.headers.get("X-Forwarded-For") or request.remote_addr or "")[:64],
        user_agent=str(request.headers.get("User-Agent") or "")[:512],
    )
    try:
        db.session.add(log)
        db.session.commit()
    except Exception:
        db.session.rollback()


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = current_admin()
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        return view(*args, **kwargs)

    return wrapped


def admin_write_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = current_admin()
        if not user:
            return jsonify({"error": "Unauthorized"}), 401

        expected = session.get(ADMIN_CSRF_KEY) or ""
        provided = str(request.headers.get("X-CSRF-Token") or "")
        if not expected or provided != expected:
            return jsonify({"error": "Invalid CSRF token"}), 403

        g.admin_user = user
        return view(*args, **kwargs)

    return wrapped
