# -*- coding: utf-8 -*-
from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app() -> Flask:
    # 读取 .env
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object("config.Config")
    app.config.update(JSON_AS_ASCII=False)

    # 初始化 DB/Migrate
    db.init_app(app)
    migrate.init_app(app, db)

    # 注册路由
    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    if os.getenv("EXPORT_WARM_ON_START", "").lower() in ("1", "true", "yes"):
        from .routes import start_export_warmup
        tables = os.getenv("EXPORT_WARM_TABLES")
        if tables:
            tables = [t.strip() for t in tables.split(",") if t.strip()]
        formats = os.getenv("EXPORT_WARM_FORMATS")
        if formats:
            formats = [f.strip() for f in formats.split(",") if f.strip()]
        start_export_warmup(app, tables, formats)

    return app

# 给 Alembic 使用（flask db 命令要能找到 db 和 models）
from . import models  # noqa: F401
