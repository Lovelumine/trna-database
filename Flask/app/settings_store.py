# -*- coding: utf-8 -*-
import json
from typing import Any

from flask import current_app
from sqlalchemy.exc import IntegrityError, OperationalError

from . import db
from .models import AppSetting


DEFAULT_DEEPSEEK_MODELS = ["deepseek-chat", "deepseek-reasoner"]
DEFAULT_OLLAMA_MODELS = ["qwen3:32b", "gemma3:27b"]
DEFAULT_AI_MAX_RETRIEVAL_ROUNDS = 2
DEFAULT_AI_MAX_TOOL_STEPS_PER_ROUND = 4
DEFAULT_AI_MAX_TOTAL_TOOL_STEPS = 12
DEFAULT_AI_RETRIEVAL_JUDGE_THRESHOLD = 0.8
DEFAULT_AI_CONVERSATION_ROUTER_TIMEOUT = 15
DEFAULT_AI_ROUTER_CONFIDENCE_THRESHOLD = 0.7

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
    "ai_workflow_enable": lambda: "1",
    "ai_conversation_router_enable": lambda: "1",
    "ai_conversation_router_model": lambda: "",
    "ai_conversation_router_timeout": lambda: str(DEFAULT_AI_CONVERSATION_ROUTER_TIMEOUT),
    "ai_router_confidence_threshold": lambda: str(DEFAULT_AI_ROUTER_CONFIDENCE_THRESHOLD),
    "ai_max_retrieval_rounds": lambda: str(DEFAULT_AI_MAX_RETRIEVAL_ROUNDS),
    "ai_max_tool_steps_per_round": lambda: str(DEFAULT_AI_MAX_TOOL_STEPS_PER_ROUND),
    "ai_max_total_tool_steps": lambda: str(DEFAULT_AI_MAX_TOTAL_TOOL_STEPS),
    "ai_retrieval_judge_enable": lambda: "1",
    "ai_retrieval_judge_model": lambda: "",
    "ai_retrieval_judge_threshold": lambda: str(DEFAULT_AI_RETRIEVAL_JUDGE_THRESHOLD),
    "ai_stop_on_no_new_evidence": lambda: "1",
    "ai_stop_on_repeated_plan": lambda: "1",
    "ai_allow_pubmed_deepen": lambda: "1",
    "ai_allow_table_deepen": lambda: "1",
    "ai_allow_doc_deepen": lambda: "1",
    "ai_final_critic_enable": lambda: "1",
    "table_column_label_overrides_json": lambda: "{}",
    "table_default_visible_columns_json": lambda: "{}",
    "table_media_field_config_json": lambda: "{}",
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
    for key, factory in DEFAULT_SETTING_FACTORIES.items():
        with db.session.no_autoflush:
            item = db.session.get(AppSetting, key)
        if item is None:
            try:
                db.session.add(AppSetting(setting_key=key, setting_value=str(factory())))
                db.session.commit()
            except IntegrityError:
                # Another worker created the row after our existence check.
                db.session.rollback()


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


def _clamp_int(value: Any, default: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(_int_text(value, default), maximum))


def _clamp_float(value: Any, default: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(_float_text(value, default), maximum))


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


def get_ai_workflow_settings() -> dict:
    ensure_default_app_settings()

    max_rounds = _clamp_int(
        get_setting("ai_max_retrieval_rounds", DEFAULT_AI_MAX_RETRIEVAL_ROUNDS),
        DEFAULT_AI_MAX_RETRIEVAL_ROUNDS,
        1,
        5,
    )
    per_round = _clamp_int(
        get_setting("ai_max_tool_steps_per_round", DEFAULT_AI_MAX_TOOL_STEPS_PER_ROUND),
        DEFAULT_AI_MAX_TOOL_STEPS_PER_ROUND,
        1,
        8,
    )
    max_total = _clamp_int(
        get_setting("ai_max_total_tool_steps", DEFAULT_AI_MAX_TOTAL_TOOL_STEPS),
        DEFAULT_AI_MAX_TOTAL_TOOL_STEPS,
        per_round,
        24,
    )
    threshold = _clamp_float(
        get_setting("ai_retrieval_judge_threshold", DEFAULT_AI_RETRIEVAL_JUDGE_THRESHOLD),
        DEFAULT_AI_RETRIEVAL_JUDGE_THRESHOLD,
        0.0,
        1.0,
    )
    router_threshold = _clamp_float(
        get_setting("ai_router_confidence_threshold", DEFAULT_AI_ROUTER_CONFIDENCE_THRESHOLD),
        DEFAULT_AI_ROUTER_CONFIDENCE_THRESHOLD,
        0.0,
        1.0,
    )
    router_timeout = _clamp_float(
        get_setting("ai_conversation_router_timeout", DEFAULT_AI_CONVERSATION_ROUTER_TIMEOUT),
        DEFAULT_AI_CONVERSATION_ROUTER_TIMEOUT,
        1.0,
        60.0,
    )

    return {
        "workflow_enable": _bool_text(get_setting("ai_workflow_enable", "1"), True),
        "conversation_router_enable": _bool_text(get_setting("ai_conversation_router_enable", "1"), True),
        "conversation_router_model": str(get_setting("ai_conversation_router_model", "") or "").strip(),
        "conversation_router_timeout": router_timeout,
        "router_confidence_threshold": router_threshold,
        "max_retrieval_rounds": max_rounds,
        "max_tool_steps_per_round": per_round,
        "max_total_tool_steps": max_total,
        "retrieval_judge_enable": _bool_text(get_setting("ai_retrieval_judge_enable", "1"), True),
        "retrieval_judge_model": str(get_setting("ai_retrieval_judge_model", "") or "").strip(),
        "retrieval_judge_threshold": threshold,
        "stop_on_no_new_evidence": _bool_text(get_setting("ai_stop_on_no_new_evidence", "1"), True),
        "stop_on_repeated_plan": _bool_text(get_setting("ai_stop_on_repeated_plan", "1"), True),
        "allow_pubmed_deepen": _bool_text(get_setting("ai_allow_pubmed_deepen", "1"), True),
        "allow_table_deepen": _bool_text(get_setting("ai_allow_table_deepen", "1"), True),
        "allow_doc_deepen": _bool_text(get_setting("ai_allow_doc_deepen", "1"), True),
        "final_critic_enable": _bool_text(get_setting("ai_final_critic_enable", "1"), True),
    }


def save_ai_workflow_settings(payload: dict):
    if not isinstance(payload, dict):
        payload = {}

    before = get_ai_workflow_settings()

    max_rounds = _clamp_int(
        payload.get("max_retrieval_rounds", before.get("max_retrieval_rounds", DEFAULT_AI_MAX_RETRIEVAL_ROUNDS)),
        DEFAULT_AI_MAX_RETRIEVAL_ROUNDS,
        1,
        5,
    )
    per_round = _clamp_int(
        payload.get("max_tool_steps_per_round", before.get("max_tool_steps_per_round", DEFAULT_AI_MAX_TOOL_STEPS_PER_ROUND)),
        DEFAULT_AI_MAX_TOOL_STEPS_PER_ROUND,
        1,
        8,
    )
    max_total = _clamp_int(
        payload.get("max_total_tool_steps", before.get("max_total_tool_steps", DEFAULT_AI_MAX_TOTAL_TOOL_STEPS)),
        DEFAULT_AI_MAX_TOTAL_TOOL_STEPS,
        per_round,
        24,
    )
    threshold = _clamp_float(
        payload.get("retrieval_judge_threshold", before.get("retrieval_judge_threshold", DEFAULT_AI_RETRIEVAL_JUDGE_THRESHOLD)),
        DEFAULT_AI_RETRIEVAL_JUDGE_THRESHOLD,
        0.0,
        1.0,
    )
    router_threshold = _clamp_float(
        payload.get("router_confidence_threshold", before.get("router_confidence_threshold", DEFAULT_AI_ROUTER_CONFIDENCE_THRESHOLD)),
        DEFAULT_AI_ROUTER_CONFIDENCE_THRESHOLD,
        0.0,
        1.0,
    )
    router_timeout = _clamp_float(
        payload.get("conversation_router_timeout", before.get("conversation_router_timeout", DEFAULT_AI_CONVERSATION_ROUTER_TIMEOUT)),
        DEFAULT_AI_CONVERSATION_ROUTER_TIMEOUT,
        1.0,
        60.0,
    )

    updates = {
        "ai_workflow_enable": "1" if bool(payload.get("workflow_enable", before.get("workflow_enable", True))) else "0",
        "ai_conversation_router_enable": "1" if bool(payload.get("conversation_router_enable", before.get("conversation_router_enable", True))) else "0",
        "ai_conversation_router_model": str(payload.get("conversation_router_model", before.get("conversation_router_model", "")) or "").strip(),
        "ai_conversation_router_timeout": str(router_timeout),
        "ai_router_confidence_threshold": str(router_threshold),
        "ai_max_retrieval_rounds": str(max_rounds),
        "ai_max_tool_steps_per_round": str(per_round),
        "ai_max_total_tool_steps": str(max_total),
        "ai_retrieval_judge_enable": "1" if bool(payload.get("retrieval_judge_enable", before.get("retrieval_judge_enable", True))) else "0",
        "ai_retrieval_judge_model": str(payload.get("retrieval_judge_model", before.get("retrieval_judge_model", "")) or "").strip(),
        "ai_retrieval_judge_threshold": str(threshold),
        "ai_stop_on_no_new_evidence": "1" if bool(payload.get("stop_on_no_new_evidence", before.get("stop_on_no_new_evidence", True))) else "0",
        "ai_stop_on_repeated_plan": "1" if bool(payload.get("stop_on_repeated_plan", before.get("stop_on_repeated_plan", True))) else "0",
        "ai_allow_pubmed_deepen": "1" if bool(payload.get("allow_pubmed_deepen", before.get("allow_pubmed_deepen", True))) else "0",
        "ai_allow_table_deepen": "1" if bool(payload.get("allow_table_deepen", before.get("allow_table_deepen", True))) else "0",
        "ai_allow_doc_deepen": "1" if bool(payload.get("allow_doc_deepen", before.get("allow_doc_deepen", True))) else "0",
        "ai_final_critic_enable": "1" if bool(payload.get("final_critic_enable", before.get("final_critic_enable", True))) else "0",
    }

    for key, value in updates.items():
        set_setting(key, value)
    db.session.commit()

    after = get_ai_workflow_settings()
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


def _normalize_media_field_config(raw: Any) -> dict[str, dict[str, Any]]:
    normalized: dict[str, dict[str, Any]] = {}
    if not isinstance(raw, dict):
        return normalized
    for field_name, config in raw.items():
        field_key = str(field_name or "").strip()
        if not field_key or not isinstance(config, dict):
            continue
        renderer = str(config.get("renderer") or "").strip().lower()
        source = str(config.get("source") or "").strip().lower()
        template = str(config.get("template") or "").strip()
        item: dict[str, Any] = {}
        if renderer in ("text", "image", "url", "file"):
            item["renderer"] = renderer
        if source in ("auto", "direct", "template"):
            item["source"] = source
        if template:
            item["template"] = template
        for key in ("width", "height"):
            try:
                value = int(config.get(key))
            except Exception:
                value = 0
            if value > 0:
                item[key] = value
        fit = str(config.get("fit") or "").strip().lower()
        if fit in ("contain", "cover", "fill"):
            item["fit"] = fit
        if "preview" in config:
            item["preview"] = bool(config.get("preview"))
        if item:
            normalized[field_key] = item
    return normalized


def get_table_media_field_config_map() -> dict[str, dict[str, dict[str, Any]]]:
    ensure_default_app_settings()
    raw = _json_dict(get_setting("table_media_field_config_json", "{}"), {})
    normalized: dict[str, dict[str, dict[str, Any]]] = {}
    for table_name, config in raw.items():
        table_key = str(table_name or "").strip()
        if not table_key:
            continue
        table_config = _normalize_media_field_config(config)
        if table_config:
            normalized[table_key] = table_config
    return normalized


def get_table_media_field_config(table: str) -> dict[str, dict[str, Any]]:
    table_key = str(table or "").strip()
    if not table_key:
        return {}
    return dict(get_table_media_field_config_map().get(table_key, {}))


def save_table_media_field_config(table: str, config: dict[str, Any]):
    table_key = str(table or "").strip()
    if not table_key:
        raise ValueError("table is required")
    before = get_table_media_field_config(table_key)
    overrides = get_table_media_field_config_map()
    normalized = _normalize_media_field_config(config)
    if normalized:
        overrides[table_key] = normalized
    else:
        overrides.pop(table_key, None)
    set_setting("table_media_field_config_json", json.dumps(overrides, ensure_ascii=False))
    db.session.commit()
    after = dict(overrides.get(table_key, {}))
    return before, after
