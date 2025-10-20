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

    return app

# 给 Alembic 使用（flask db 命令要能找到 db 和 models）
from . import models  # noqa: F401
