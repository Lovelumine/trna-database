# -*- coding: utf-8 -*-
from . import db
from sqlalchemy import func

class EnsureRecord(db.Model):
    __tablename__ = "ensure_record"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    ensure_id = db.Column(db.String(128), index=True, nullable=False)  # 如果经常很长可改 VARCHAR(256/512) 或 TEXT
    pmid      = db.Column(db.String(32), index=True)
    title     = db.Column(db.String(512))
    payload   = db.Column(db.Text)  # 长文本/JSON
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
