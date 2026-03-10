# -*- coding: utf-8 -*-
from . import db
from sqlalchemy import func, text

class EnsureRecord(db.Model):
    __tablename__ = "ensure_record"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    ensure_id = db.Column(db.String(128), index=True, nullable=False)  # 如果经常很长可改 VARCHAR(256/512) 或 TEXT
    pmid      = db.Column(db.String(32), index=True)
    title     = db.Column(db.String(512))
    payload   = db.Column(db.Text)  # 长文本/JSON
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())


class AdminUser(db.Model):
    __tablename__ = "admin_users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(32), nullable=False, server_default=text("'admin'"))
    is_active = db.Column(db.Boolean, nullable=False, server_default=text("1"))
    last_login_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())


class AdminAuditLog(db.Model):
    __tablename__ = "admin_audit_logs"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, index=True)
    username = db.Column(db.String(64), index=True)
    role = db.Column(db.String(32))
    action = db.Column(db.String(64), nullable=False, index=True)
    table_name = db.Column(db.String(128), index=True)
    record_pk = db.Column(db.String(255), index=True)
    before_json = db.Column(db.Text)
    after_json = db.Column(db.Text)
    ip_address = db.Column(db.String(64))
    user_agent = db.Column(db.String(512))
    created_at = db.Column(db.DateTime, server_default=func.now(), index=True)


class AppSetting(db.Model):
    __tablename__ = "app_settings"

    setting_key = db.Column(db.String(128), primary_key=True)
    setting_value = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
