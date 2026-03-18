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


class MediaAsset(db.Model):
    __tablename__ = "media_assets"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    bucket = db.Column(db.String(128), nullable=False, index=True)
    object_key = db.Column(db.String(512), nullable=False, unique=True, index=True)
    public_url = db.Column(db.String(1024), nullable=False)
    mime_type = db.Column(db.String(128), nullable=False)
    file_ext = db.Column(db.String(32), nullable=False)
    size_bytes = db.Column(db.BigInteger, nullable=False, server_default=text("0"))
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    sha256 = db.Column(db.String(64), index=True)
    title = db.Column(db.String(255))
    alt_text = db.Column(db.String(255))
    original_filename = db.Column(db.String(255))
    source_type = db.Column(db.String(64), nullable=False, server_default=text("'library'"), index=True)
    created_by = db.Column(db.Integer, index=True)
    created_by_username = db.Column(db.String(64), index=True)
    created_at = db.Column(db.DateTime, server_default=func.now(), index=True)


class MediaBinding(db.Model):
    __tablename__ = "media_bindings"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    asset_id = db.Column(db.BigInteger, db.ForeignKey("media_assets.id", ondelete="CASCADE"), nullable=False, index=True)
    binding_type = db.Column(db.String(64), nullable=False, index=True)
    binding_key = db.Column(db.String(64), nullable=False, server_default=text("''"))
    resource_name = db.Column(db.String(255), nullable=False, index=True)
    field_name = db.Column(db.String(255), nullable=False, server_default=text("''"))
    record_key = db.Column(db.String(255), nullable=False, server_default=text("''"), index=True)
    slot_key = db.Column(db.String(255), nullable=False, server_default=text("''"), index=True)
    extra_json = db.Column(db.Text)
    created_by = db.Column(db.Integer, index=True)
    created_by_username = db.Column(db.String(64), index=True)
    created_at = db.Column(db.DateTime, server_default=func.now(), index=True)

    __table_args__ = (
        db.UniqueConstraint(
            "asset_id",
            "binding_key",
            name="uq_media_binding_location",
        ),
    )
