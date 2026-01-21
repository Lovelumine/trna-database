# -*- coding: utf-8 -*-
import os
from urllib.parse import quote_plus

class Config:
    # 优先用 DATABASE_URL，否则用分段变量拼
    _db_url = os.getenv("DATABASE_URL")
    if not _db_url:
        user = os.getenv("MYSQL_USER", "root")
        pwd  = os.getenv("MYSQL_PASSWORD", "")
        host = os.getenv("MYSQL_HOST", "127.0.0.1")
        port = int(os.getenv("MYSQL_PORT", "3306"))
        db   = os.getenv("MYSQL_DB", "test")
        # 使用 utf8mb4；pool_pre_ping 保活；pool_recycle 避免长连接被踢
        _db_url = (
            f"mysql+pymysql://{quote_plus(user)}:{quote_plus(pwd)}@{host}:{port}/{db}"
            "?charset=utf8mb4"
        )

    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 1800,
        "pool_size": 5,
        "max_overflow": 10,
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    EXPORT_CACHE_DIR = os.getenv(
        "EXPORT_CACHE_DIR",
        os.path.join(os.path.dirname(__file__), "app", "cache", "exports"),
    )
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
    MINIO_BUCKET = os.getenv("MINIO_BUCKET")
    MINIO_EXPORT_PREFIX = os.getenv("MINIO_EXPORT_PREFIX", "exports")
    MINIO_PUBLIC_BASE = os.getenv("MINIO_PUBLIC_BASE")
    _minio_secure = os.getenv("MINIO_SECURE")
    if _minio_secure is None:
        MINIO_SECURE = None
    else:
        MINIO_SECURE = _minio_secure.strip().lower() in ("1", "true", "yes")

    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://192.168.236.2:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:32b")
    OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "120"))
    OLLAMA_SYSTEM_PROMPT = os.getenv(
        "OLLAMA_SYSTEM_PROMPT",
        (
            "You are Yingying (荧荧), the AI assistant for ENSURE.\n"
            "Identity: Always present yourself as Yingying. Do not mention or reveal any model, "
            "provider, or backend details. Never say you are an AI model.\n"
            "Language: If the user asks in Chinese, answer in Chinese; otherwise answer in English. "
            "When answering in Chinese, keep scientific terms and key names in English when natural.\n"
            "About ENSURE: ENSURE (https://trna.lumoxuan.cn/) is the Encyclopedia of Suppressor tRNA "
            "with an AI assistant. It is a comprehensive database for suppressor tRNA research, "
            "covering disease- and cancer-associated nonsense/missense/frameshift variants, natural "
            "sup-tRNAs, engineered tRNA strategies, and curated tRNA elements. Data include multiple "
            "sequence alignment, secondary structure prediction, and AlphaFold 3 modeling with "
            "interactive 2D/3D visualization. ENSURE supports keyword search, BLAST, and bulk download.\n"
            "Key publication: ENSURE: the Encyclopedia of Suppressor tRNA with an AI assistant. "
            "PMID 41160884, DOI 10.1093/nar/gkaf1062.\n"
            "Capabilities: Answer questions about ENSURE, its website and platform features, and help "
            "retrieve or interpret database content. If a question requires specific records or exact "
            "statistics, ask for clarification or request the user to specify what to search."
        ),
    )
    OLLAMA_MAX_MESSAGES = int(os.getenv("OLLAMA_MAX_MESSAGES", "20"))
