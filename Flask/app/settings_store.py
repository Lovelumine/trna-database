# -*- coding: utf-8 -*-
import json
from typing import Any

from flask import current_app
from sqlalchemy.exc import OperationalError

from . import db
from .models import AppSetting


DEFAULT_DEEPSEEK_MODELS = ["deepseek-chat", "deepseek-reasoner"]
DEFAULT_OLLAMA_MODELS = ["qwen3:32b", "gemma3:27b"]

DEFAULT_SETTING_FACTORIES = {
    "llm_active_provider": lambda: "ollama",
    "llm_active_model": lambda: str(current_app.config.get("OLLAMA_MODEL") or "qwen3:32b"),
    "llm_timeout": lambda: str(current_app.config.get("OLLAMA_TIMEOUT") or 120),
    "llm_max_messages": lambda: str(current_app.config.get("OLLAMA_MAX_MESSAGES") or 20),
    "llm_system_prompt": lambda: str(current_app.config.get("OLLAMA_SYSTEM_PROMPT") or ""),
    "llm_ollama_base_url": lambda: str(current_app.config.get("OLLAMA_BASE_URL") or "http://127.0.0.1:11434"),
    "llm_ollama_default_model": lambda: str(current_app.config.get("OLLAMA_MODEL") or "qwen3:32b"),
    "llm_ollama_models_json": lambda: json.dumps(DEFAULT_OLLAMA_MODELS, ensure_ascii=False),
    "llm_deepseek_base_url": lambda: str(current_app.config.get("DEEPSEEK_BASE_URL") or "https://api.deepseek.com"),
    "llm_deepseek_api_key": lambda: str(current_app.config.get("DEEPSEEK_API_KEY") or ""),
    "llm_deepseek_default_model": lambda: str(current_app.config.get("DEEPSEEK_MODEL") or "deepseek-chat"),
    "llm_deepseek_models_json": lambda: json.dumps(DEFAULT_DEEPSEEK_MODELS, ensure_ascii=False),
    "table_column_label_overrides_json": lambda: "{}",
    "table_default_visible_columns_json": lambda: "{}",
}


def ensure_app_settings_table():
    try:
        AppSetting.__table__.create(bind=db.engine, checkfirst=True)
    except OperationalError as exc:
        message = str(exc).lower()
        if "already exists" not in message:
            raise


def ensure_default_app_settings():
    ensure_app_settings_table()
    changed = False
    for key, factory in DEFAULT_SETTING_FACTORIES.items():
        item = db.session.get(AppSetting, key)
        if item is None:
            item = AppSetting(setting_key=key, setting_value=str(factory()))
            db.session.add(item)
            changed = True
    if changed:
        db.session.commit()


def get_setting(key: str, default: Any = ""):
    item = db.session.get(AppSetting, key)
    if item is None:
        return default
    return item.setting_value if item.setting_value is not None else default


def set_setting(key: str, value: Any):
    item = db.session.get(AppSetting, key)
    if item is None:
        item = AppSetting(setting_key=key)
    item.setting_value = "" if value is None else str(value)
    db.session.add(item)
    return item


def _json_list(raw: Any, fallback: list[str]) -> list[str]:
    try:
        data = json.loads(str(raw or "").strip() or "[]")
    except Exception:
        data = []
    if not isinstance(data, list):
        return list(fallback)
    values = []
    for item in data:
        text = str(item or "").strip()
        if text and text not in values:
            values.append(text)
    return values or list(fallback)


def _json_dict(raw: Any, fallback: dict | None = None) -> dict:
    try:
        data = json.loads(str(raw or "").strip() or "{}")
    except Exception:
        data = {}
    if not isinstance(data, dict):
        return dict(fallback or {})
    return data


def _bool_text(raw: Any, default: bool) -> bool:
    text = str(raw or "").strip().lower()
    if not text:
        return default
    return text in ("1", "true", "yes", "on")


def _float_text(raw: Any, default: float) -> float:
    try:
        return float(raw)
    except Exception:
        return float(default)


def _int_text(raw: Any, default: int) -> int:
    try:
        return int(raw)
    except Exception:
        return int(default)


def get_llm_settings(include_secrets: bool = False) -> dict:
    ensure_default_app_settings()

    default_system_prompt = str(current_app.config.get("OLLAMA_SYSTEM_PROMPT") or "").strip()

    active_provider = str(get_setting("llm_active_provider", "ollama") or "ollama").strip().lower()
    active_model = str(get_setting("llm_active_model", "") or "").strip()

    ollama_models = _json_list(
        get_setting("llm_ollama_models_json", ""),
        DEFAULT_OLLAMA_MODELS,
    )
    deepseek_models = _json_list(
        get_setting("llm_deepseek_models_json", ""),
        DEFAULT_DEEPSEEK_MODELS,
    )

    if active_provider not in ("ollama", "deepseek"):
        active_provider = "ollama"

    if not active_model:
        active_model = (
            str(get_setting("llm_deepseek_default_model", "deepseek-chat"))
            if active_provider == "deepseek"
            else str(get_setting("llm_ollama_default_model", "qwen3:32b"))
        )

    model_options = []
    for name in ollama_models + deepseek_models:
        if name not in model_options:
            model_options.append(name)
    if active_model and active_model not in model_options:
        model_options.insert(0, active_model)

    data = {
        "active_provider": active_provider,
        "active_model": active_model,
        "timeout": _float_text(get_setting("llm_timeout", 120), 120),
        "max_messages": _int_text(get_setting("llm_max_messages", 20), 20),
        "system_prompt": str(get_setting("llm_system_prompt", default_system_prompt) or "").strip() or default_system_prompt,
        "ollama_base_url": str(get_setting("llm_ollama_base_url", "http://127.0.0.1:11434") or "").strip(),
        "ollama_default_model": str(get_setting("llm_ollama_default_model", "qwen3:32b") or "").strip(),
        "ollama_models": ollama_models,
        "deepseek_base_url": str(get_setting("llm_deepseek_base_url", "https://api.deepseek.com") or "").strip(),
        "deepseek_default_model": str(get_setting("llm_deepseek_default_model", "deepseek-chat") or "").strip(),
        "deepseek_models": deepseek_models,
        "model_options": model_options,
    }
    if include_secrets:
        data["deepseek_api_key"] = str(get_setting("llm_deepseek_api_key", "") or "").strip()
    else:
        value = str(get_setting("llm_deepseek_api_key", "") or "").strip()
        data["deepseek_api_key_masked"] = value[:6] + "..." + value[-4:] if len(value) > 12 else ("***" if value else "")
    return data


def save_llm_settings(payload: dict):
    if not isinstance(payload, dict):
        payload = {}

    def _csv_or_list_to_json(value: Any, fallback: list[str]) -> str:
        if isinstance(value, list):
            items = [str(item or "").strip() for item in value if str(item or "").strip()]
        else:
            items = [part.strip() for part in str(value or "").replace("\n", ",").split(",") if part.strip()]
        dedup = []
        for item in items:
            if item not in dedup:
                dedup.append(item)
        return json.dumps(dedup or fallback, ensure_ascii=False)

    updates = {
        "llm_active_provider": str(payload.get("active_provider") or "ollama").strip().lower(),
        "llm_active_model": str(payload.get("active_model") or "").strip(),
        "llm_timeout": str(payload.get("timeout") or "120").strip(),
        "llm_max_messages": str(payload.get("max_messages") or "20").strip(),
        "llm_system_prompt": str(payload.get("system_prompt") or ""),
        "llm_ollama_base_url": str(payload.get("ollama_base_url") or "").strip(),
        "llm_ollama_default_model": str(payload.get("ollama_default_model") or "").strip(),
        "llm_ollama_models_json": _csv_or_list_to_json(payload.get("ollama_models"), DEFAULT_OLLAMA_MODELS),
        "llm_deepseek_base_url": str(payload.get("deepseek_base_url") or "").strip(),
        "llm_deepseek_default_model": str(payload.get("deepseek_default_model") or "").strip(),
        "llm_deepseek_models_json": _csv_or_list_to_json(payload.get("deepseek_models"), DEFAULT_DEEPSEEK_MODELS),
    }

    if "deepseek_api_key" in payload:
        updates["llm_deepseek_api_key"] = str(payload.get("deepseek_api_key") or "").strip()

    provider = updates["llm_active_provider"]
    if provider not in ("ollama", "deepseek"):
        provider = "ollama"
        updates["llm_active_provider"] = provider

    if not updates["llm_active_model"]:
        updates["llm_active_model"] = (
            updates["llm_deepseek_default_model"] if provider == "deepseek" else updates["llm_ollama_default_model"]
        )

    before = get_llm_settings(include_secrets=True)
    for key, value in updates.items():
        set_setting(key, value)
    db.session.commit()
    after = get_llm_settings(include_secrets=True)
    return before, after


def get_table_column_label_overrides() -> dict[str, dict[str, str]]:
    ensure_default_app_settings()
    raw = _json_dict(get_setting("table_column_label_overrides_json", "{}"), {})
    normalized: dict[str, dict[str, str]] = {}
    for table_name, labels in raw.items():
        if not isinstance(labels, dict):
            continue
        table_key = str(table_name or "").strip()
        if not table_key:
            continue
        table_labels: dict[str, str] = {}
        for column_name, label in labels.items():
            column_key = str(column_name or "").strip()
            text = str(label or "").strip()
            if column_key and text:
                table_labels[column_key] = text
        if table_labels:
            normalized[table_key] = table_labels
    return normalized


def get_table_column_labels(table: str) -> dict[str, str]:
    table_key = str(table or "").strip()
    if not table_key:
        return {}
    return dict(get_table_column_label_overrides().get(table_key, {}))


def save_table_column_labels(table: str, labels: dict[str, Any]):
    table_key = str(table or "").strip()
    if not table_key:
        raise ValueError("table is required")
    before = get_table_column_labels(table_key)
    overrides = get_table_column_label_overrides()
    normalized: dict[str, str] = {}
    if isinstance(labels, dict):
        for column_name, label in labels.items():
            column_key = str(column_name or "").strip()
            text = str(label or "").strip()
            if column_key and text:
                normalized[column_key] = text
    if normalized:
        overrides[table_key] = normalized
    else:
        overrides.pop(table_key, None)
    set_setting("table_column_label_overrides_json", json.dumps(overrides, ensure_ascii=False))
    db.session.commit()
    after = dict(overrides.get(table_key, {}))
    return before, after


def get_table_default_visible_columns_map() -> dict[str, list[str]]:
    ensure_default_app_settings()
    raw = _json_dict(get_setting("table_default_visible_columns_json", "{}"), {})
    normalized: dict[str, list[str]] = {}
    for table_name, columns in raw.items():
        table_key = str(table_name or "").strip()
        if not table_key or not isinstance(columns, list):
            continue
        visible_columns: list[str] = []
        for column_name in columns:
            column_key = str(column_name or "").strip()
            if column_key and column_key not in visible_columns:
                visible_columns.append(column_key)
        if visible_columns:
            normalized[table_key] = visible_columns
    return normalized


def get_table_default_visible_columns(table: str) -> list[str]:
    table_key = str(table or "").strip()
    if not table_key:
        return []
    return list(get_table_default_visible_columns_map().get(table_key, []))


def save_table_default_visible_columns(table: str, columns: list[Any]):
    table_key = str(table or "").strip()
    if not table_key:
        raise ValueError("table is required")
    before = get_table_default_visible_columns(table_key)
    overrides = get_table_default_visible_columns_map()
    normalized: list[str] = []
    if isinstance(columns, list):
        for column_name in columns:
            column_key = str(column_name or "").strip()
            if column_key and column_key not in normalized:
                normalized.append(column_key)
    if normalized:
        overrides[table_key] = normalized
    else:
        overrides.pop(table_key, None)
    set_setting("table_default_visible_columns_json", json.dumps(overrides, ensure_ascii=False))
    db.session.commit()
    after = list(overrides.get(table_key, []))
    return before, after
