from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import requests
from flask import Flask


FLASK_ROOT = Path(__file__).resolve().parents[1]
if str(FLASK_ROOT) not in sys.path:
    sys.path.insert(0, str(FLASK_ROOT))

from app import routes, settings_store  # noqa: E402


def build_test_app(register_routes: bool = False) -> Flask:
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret",
        TOOL_ROUTER_ENABLE=True,
        TOOL_ROUTER_MAX_STEPS=8,
        TOOL_ROUTER_TIMEOUT=20,
        TOOL_RESULT_MAX_CHARS=2000,
        LANG_DETECT_ENABLE=False,
        INTENT_ROUTER_ENABLE=False,
        RAG_ENABLE=True,
        STRICT_EVIDENCE_MODE=False,
    )
    if register_routes:
        app.register_blueprint(routes.bp)
    return app


@pytest.fixture()
def app_ctx():
    app = build_test_app()
    with app.app_context():
        yield app


def test_xiaomi_llm_settings_roundtrip(app_ctx: Flask, monkeypatch: pytest.MonkeyPatch):
    store = {
        "llm_active_provider": "xiaomi",
        "llm_active_model": "",
        "llm_timeout": "120",
        "llm_max_messages": "20",
        "llm_system_prompt": "You are Yingying.",
        "llm_ollama_base_url": "http://127.0.0.1:11434",
        "llm_ollama_default_model": "",
        "llm_ollama_models_json": "[]",
        "llm_deepseek_base_url": "https://api.deepseek.com",
        "llm_deepseek_api_key": "test-deepseek-key",
        "llm_deepseek_default_model": "deepseek-v4-pro",
        "llm_deepseek_models_json": '["deepseek-v4-pro"]',
        "llm_xiaomi_base_url": "https://api.xiaomimimo.com/v1",
        "llm_xiaomi_api_key": "test-xiaomi-key",
        "llm_xiaomi_default_model": "mimo-v2.5-pro",
        "llm_xiaomi_models_json": '["mimo-v2.5-pro"]',
    }

    monkeypatch.setattr(settings_store, "ensure_default_app_settings", lambda: None)
    monkeypatch.setattr(settings_store, "get_setting", lambda key, default="": store.get(key, default))
    monkeypatch.setattr(settings_store, "set_setting", lambda key, value: store.__setitem__(key, "" if value is None else str(value)))
    monkeypatch.setattr(settings_store, "db", SimpleNamespace(session=SimpleNamespace(commit=lambda: None)))

    initial = settings_store.get_llm_settings(include_secrets=True)
    assert initial["active_provider"] == "xiaomi"
    assert initial["active_model"] == "mimo-v2.5-pro"
    assert initial["xiaomi_models"] == ["mimo-v2.5-pro"]
    assert initial["xiaomi_api_key"] == "test-xiaomi-key"

    _, updated = settings_store.save_llm_settings(
        {
            "active_provider": "xiaomi",
            "active_model": "mimo-v2.5-pro",
            "timeout": 90,
            "max_messages": 16,
            "system_prompt": "You are Yingying.",
            "ollama_base_url": "http://127.0.0.1:11434",
            "ollama_default_model": "",
            "ollama_models": [],
            "deepseek_base_url": "https://api.deepseek.com",
            "deepseek_default_model": "deepseek-v4-pro",
            "deepseek_models": ["deepseek-v4-pro"],
            "xiaomi_base_url": "https://api.xiaomimimo.com/v1",
            "xiaomi_api_key": "replacement-test-key",
            "xiaomi_default_model": "mimo-v2.5-pro",
            "xiaomi_models": ["mimo-v2.5-pro"],
        }
    )

    assert updated["active_provider"] == "xiaomi"
    assert updated["active_model"] == "mimo-v2.5-pro"
    assert updated["xiaomi_api_key"] == "replacement-test-key"
    assert store["llm_xiaomi_base_url"] == "https://api.xiaomimimo.com/v1"


def test_llm_audit_redaction_removes_provider_keys():
    original = {
        "active_provider": "xiaomi",
        "deepseek_api_key": "test-deepseek-secret",
        "xiaomi_api_key": "test-xiaomi-secret",
    }

    redacted = settings_store.redact_llm_settings_for_audit(original)
    serialized = json.dumps(redacted)

    assert original["xiaomi_api_key"] == "test-xiaomi-secret"
    assert redacted["deepseek_api_key"] == "[REDACTED]"
    assert redacted["xiaomi_api_key"] == "[REDACTED]"
    assert "test-deepseek-secret" not in serialized
    assert "test-xiaomi-secret" not in serialized


def test_embedding_rebuild_requires_admin_session():
    app = build_test_app(register_routes=True)

    with app.test_client() as client:
        response = client.post("/embedding/rebuild")

    assert response.status_code == 401
    assert response.get_json() == {"error": "Unauthorized"}


def test_chat_title_keeps_ensure_database_context(monkeypatch: pytest.MonkeyPatch):
    app = build_test_app(register_routes=True)
    captured = {}
    runtime = {"provider": "xiaomi", "model": "mimo-v2.5-pro"}

    monkeypatch.setattr(routes, "_get_llm_runtime", lambda requested_model="": runtime)
    monkeypatch.setattr(routes, "_select_chat_model", lambda requested_model, default_model: default_model)

    def fake_stream(actual_runtime, messages, model=""):
        captured["messages"] = messages
        captured["model"] = model
        return iter([("ENSURE Database Purpose", True)])

    monkeypatch.setattr(routes, "_llm_stream", fake_stream)

    with app.test_client() as client:
        response = client.post(
            "/chat/api/title",
            json={"messages": [{"role": "user", "content": "What is ENSURE used for?"}]},
        )

    assert response.status_code == 200
    assert response.get_json() == {"title": "ENSURE Database Purpose"}
    system_prompt = captured["messages"][0]["content"]
    assert "Encyclopedia of Suppressor tRNA" in system_prompt
    assert "Do not answer" in system_prompt
    assert captured["model"] == "mimo-v2.5-pro"


def test_xiaomi_runtime_is_selected_by_model(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        routes,
        "get_llm_settings",
        lambda include_secrets=True: {
            "active_provider": "deepseek",
            "active_model": "deepseek-v4-pro",
            "timeout": 120,
            "max_messages": 20,
            "system_prompt": "You are Yingying.",
            "ollama_base_url": "http://127.0.0.1:11434",
            "ollama_models": [],
            "deepseek_base_url": "https://api.deepseek.com",
            "deepseek_api_key": "test-deepseek-key",
            "deepseek_default_model": "deepseek-v4-pro",
            "deepseek_models": ["deepseek-v4-pro"],
            "xiaomi_base_url": "https://api.xiaomimimo.com/v1",
            "xiaomi_api_key": "test-xiaomi-key",
            "xiaomi_default_model": "mimo-v2.5-pro",
            "xiaomi_models": ["mimo-v2.5-pro"],
            "model_options": ["deepseek-v4-pro", "mimo-v2.5-pro"],
        },
    )

    runtime = routes._get_llm_runtime("mimo-v2.5-pro")

    assert runtime["provider"] == "xiaomi"
    assert runtime["model"] == "mimo-v2.5-pro"
    assert runtime["xiaomi_base_url"] == "https://api.xiaomimimo.com/v1"


def test_xiaomi_once_uses_openai_compatible_request(monkeypatch: pytest.MonkeyPatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"message": {"content": "MiMo response"}}]}

    def fake_post(url, **kwargs):
        captured["url"] = url
        captured.update(kwargs)
        return FakeResponse()

    monkeypatch.setattr(routes.requests, "post", fake_post)

    answer = routes._xiaomi_once(
        "https://api.xiaomimimo.com/v1/",
        "test-xiaomi-key",
        "mimo-v2.5-pro",
        [{"role": "user", "content": "Hello"}],
        30,
        {"thinking_enabled": False, "reasoning_effort": "max"},
    )

    assert answer == "MiMo response"
    assert captured["url"] == "https://api.xiaomimimo.com/v1/chat/completions"
    assert captured["headers"]["Authorization"] == "Bearer test-xiaomi-key"
    assert captured["json"]["model"] == "mimo-v2.5-pro"
    assert captured["json"]["stream"] is False
    assert captured["json"]["thinking"] == {"type": "disabled"}
    assert "reasoning_effort" not in captured["json"]


def test_xiaomi_stream_parses_openai_compatible_sse(monkeypatch: pytest.MonkeyPatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def iter_lines(self, decode_unicode=False):
            assert decode_unicode is True
            return iter(
                [
                    'data: {"choices":[{"delta":{"content":"Mi"},"finish_reason":null}]}',
                    'data: {"choices":[{"delta":{"content":"Mo"},"finish_reason":"stop"}]}',
                    "data: [DONE]",
                ]
            )

    response = FakeResponse()

    def fake_post(url, **kwargs):
        captured["url"] = url
        captured.update(kwargs)
        return response

    monkeypatch.setattr(routes.requests, "post", fake_post)

    chunks = list(
        routes._xiaomi_stream(
            "https://api.xiaomimimo.com/v1",
            "test-xiaomi-key",
            "mimo-v2.5-pro",
            [{"role": "user", "content": "Hello"}],
            30,
            {"thinking_enabled": True, "reasoning_effort": "max"},
        )
    )

    assert chunks[:2] == [("Mi", False), ("Mo", True)]
    assert captured["stream"] is True
    assert captured["json"]["stream"] is True
    assert captured["json"]["thinking"] == {"type": "enabled"}
    assert "reasoning_effort" not in captured["json"]
    assert response.encoding == "utf-8"


def test_visible_answer_recovers_from_mimo_tool_markup(monkeypatch: pytest.MonkeyPatch):
    replies = iter(
        [
            "好的。<function=query_db><parameter=sql>SELECT * FROM secret_table",
            "ENSURE contains curated suppressor tRNA records [S1].",
        ]
    )
    captured_messages = []

    def fake_once(runtime, messages, model="", timeout=None):
        captured_messages.append(messages)
        return next(replies)

    monkeypatch.setattr(routes, "_llm_once", fake_once)

    answer = routes._llm_visible_once(
        {"provider": "xiaomi", "model": "mimo-v2.5-pro"},
        [{"role": "user", "content": "介绍数据库"}],
        "介绍数据库",
    )

    assert answer == "ENSURE contains curated suppressor tRNA records [S1]."
    assert len(captured_messages) == 2
    assert "previous draft was rejected" in captured_messages[1][-1]["content"]
    assert "SELECT" not in answer
    assert "<function" not in answer


def test_mimo_payment_error_falls_back_to_configured_deepseek(monkeypatch: pytest.MonkeyPatch):
    response = requests.Response()
    response.status_code = 402
    payment_error = requests.HTTPError("payment required", response=response)
    monkeypatch.setattr(routes, "_xiaomi_once", lambda *args, **kwargs: (_ for _ in ()).throw(payment_error))
    monkeypatch.setattr(
        routes,
        "_get_llm_runtime",
        lambda requested_model="", requested_provider="": {
            "provider": "deepseek",
            "model": "deepseek-v4-pro",
            "deepseek_base_url": "https://api.deepseek.com",
            "deepseek_api_key": "configured",
        },
    )
    captured = {}

    def fake_deepseek(base, api_key, model, messages, timeout, runtime=None):
        captured.update({"model": model, "thinking": runtime.get("thinking_enabled")})
        return "fallback answer"

    monkeypatch.setattr(routes, "_deepseek_once", fake_deepseek)
    app = build_test_app()
    with app.app_context():
        answer = routes._llm_once(
            {
                "provider": "xiaomi",
                "model": "mimo-v2.5-pro",
                "xiaomi_api_key": "configured",
                "thinking_enabled": True,
            },
            [{"role": "user", "content": "hello"}],
        )

    assert answer == "fallback answer"
    assert captured == {"model": "deepseek-v4-pro", "thinking": True}


def test_generic_database_introduction_gets_deterministic_sample_plan():
    plan = routes._augment_plan_with_heuristics(
        [],
        "从这个数据库找点东西给我介绍",
        1,
    )

    assert plan == [
        {
            "tool": "table_rows",
            "params": {"table": "Engineered_sup_tRNA", "page": 1, "page_size": 3},
        }
    ]


def test_visible_answer_blocks_repeated_mimo_tool_markup(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        routes,
        "_llm_once",
        lambda *args, **kwargs: "<function=query_db><parameter=sql>SELECT COUNT(*) FROM users",
    )

    answer = routes._llm_visible_once(
        {"provider": "xiaomi", "model": "mimo-v2.5-pro"},
        [{"role": "user", "content": "从数据库里找点内容"}],
        "从数据库里找点内容",
    )

    assert answer == "本次回答包含了不应展示的内部调用信息，已被安全拦截。请您重试一次。"
    assert "SELECT" not in answer
    assert not routes._contains_internal_tool_markup("The result was significant (p < 0.05).")
    assert routes._contains_internal_tool_markup("\nSELECT COUNT(*) AS cnt FROM private_table")
    assert not routes._contains_internal_tool_markup("Select records from the evidence table below.")


def test_client_history_drops_leaked_assistant_tool_markup():
    history = routes._normalize_client_history(
        [
            {"role": "user", "content": "介绍数据库"},
            {"role": "assistant", "content": "<function=query_db><parameter=sql>SELECT * FROM private"},
            {"role": "assistant", "content": "A safe previous answer."},
        ],
        20,
    )

    assert history == [
        {"role": "user", "content": "介绍数据库"},
        {"role": "assistant", "content": "A safe previous answer."},
    ]


def test_database_question_bypasses_ai_router_for_required_retrieval(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        routes,
        "_llm_once",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("router should be bypassed")),
    )

    decision = routes._route_conversation_request(
        {"provider": "xiaomi", "model": "mimo-v2.5-pro", "timeout": 120},
        "mimo-v2.5-pro",
        [{"role": "user", "content": "从这个数据库找点东西给我介绍"}],
        "从这个数据库找点东西给我介绍",
        {"conversation_router_enable": True, "router_confidence_threshold": 0.7},
        "explain",
        True,
    )

    assert decision["route"] == "knowledge_retrieval"
    assert decision["reason"] == "evidence_required_retrieval"


def test_anonymous_chat_cookie_separates_visitors_and_binds_chat_ids():
    app = build_test_app(register_routes=True)
    visitor_a = app.test_client()
    visitor_b = app.test_client()

    identity_a = visitor_a.get("/chat/api/identity", base_url="https://trna.example")
    namespace_a = identity_a.get_json()["data"]["storage_namespace"]
    cookie_header = identity_a.headers.get("Set-Cookie", "")
    assert "ensure_chat_visitor=" in cookie_header
    assert "HttpOnly" in cookie_header
    assert "Secure" in cookie_header
    assert "SameSite=Lax" in cookie_header

    open_a = visitor_a.get("/chat/api/open", base_url="https://trna.example")
    chat_id_a = open_a.get_json()["data"]
    assert chat_id_a.startswith("v1.")

    identity_b = visitor_b.get("/chat/api/identity", base_url="https://trna.example")
    namespace_b = identity_b.get_json()["data"]["storage_namespace"]
    assert namespace_b != namespace_a

    cross_visitor = visitor_b.post(
        f"/chat/api/chat_message/{chat_id_a}",
        base_url="https://trna.example",
        json={"message": "hello"},
    )
    assert cross_visitor.status_code == 404
    assert cross_visitor.get_json() == {"error": "chat session not found"}

    tampered = chat_id_a[:-1] + ("0" if chat_id_a[-1] != "0" else "1")
    tampered_response = visitor_a.post(
        f"/chat/api/chat_message/{tampered}",
        base_url="https://trna.example",
        json={"message": "hello"},
    )
    assert tampered_response.status_code == 404


def test_ai_workflow_settings_roundtrip(app_ctx: Flask, monkeypatch: pytest.MonkeyPatch):
    store = {
        "ai_workflow_enable": "1",
        "ai_conversation_router_enable": "1",
        "ai_conversation_router_model": "",
        "ai_conversation_router_timeout": "15",
        "ai_router_confidence_threshold": "0.7",
        "ai_max_retrieval_rounds": "2",
        "ai_max_tool_steps_per_round": "4",
        "ai_max_total_tool_steps": "12",
        "ai_retrieval_judge_enable": "1",
        "ai_retrieval_judge_model": "",
        "ai_retrieval_judge_threshold": "0.8",
        "ai_stop_on_no_new_evidence": "1",
        "ai_stop_on_repeated_plan": "1",
        "ai_allow_pubmed_deepen": "1",
        "ai_allow_table_deepen": "1",
        "ai_allow_doc_deepen": "1",
        "ai_final_critic_enable": "1",
    }

    monkeypatch.setattr(settings_store, "ensure_default_app_settings", lambda: None)
    monkeypatch.setattr(settings_store, "get_setting", lambda key, default="": store.get(key, default))
    monkeypatch.setattr(settings_store, "set_setting", lambda key, value: store.__setitem__(key, "" if value is None else str(value)))
    monkeypatch.setattr(settings_store, "db", SimpleNamespace(session=SimpleNamespace(commit=lambda: None)))

    defaults = settings_store.get_ai_workflow_settings()
    assert defaults["workflow_enable"] is True
    assert defaults["conversation_router_enable"] is True
    assert defaults["conversation_router_model"] == ""
    assert defaults["conversation_router_timeout"] == 15
    assert defaults["router_confidence_threshold"] == 0.7
    assert defaults["max_retrieval_rounds"] == 2
    assert defaults["max_tool_steps_per_round"] == 4
    assert defaults["max_total_tool_steps"] == 12

    before, after = settings_store.save_ai_workflow_settings(
        {
            "workflow_enable": False,
            "conversation_router_enable": False,
            "conversation_router_model": "deepseek-reasoner",
            "conversation_router_timeout": 90,
            "router_confidence_threshold": 1.2,
            "max_retrieval_rounds": 9,
            "max_tool_steps_per_round": 10,
            "max_total_tool_steps": 99,
            "retrieval_judge_enable": False,
            "retrieval_judge_model": "deepseek-reasoner",
            "retrieval_judge_threshold": 1.5,
            "stop_on_no_new_evidence": False,
            "stop_on_repeated_plan": False,
            "allow_pubmed_deepen": False,
            "allow_table_deepen": True,
            "allow_doc_deepen": False,
            "final_critic_enable": False,
        }
    )

    assert before["workflow_enable"] is True
    assert after["workflow_enable"] is False
    assert after["conversation_router_enable"] is False
    assert after["conversation_router_model"] == "deepseek-reasoner"
    assert after["conversation_router_timeout"] == 60.0
    assert after["router_confidence_threshold"] == 1.0
    assert after["max_retrieval_rounds"] == 5
    assert after["max_tool_steps_per_round"] == 8
    assert after["max_total_tool_steps"] == 24
    assert after["retrieval_judge_enable"] is False
    assert after["retrieval_judge_model"] == "deepseek-reasoner"
    assert after["retrieval_judge_threshold"] == 1.0
    assert after["stop_on_no_new_evidence"] is False
    assert after["stop_on_repeated_plan"] is False
    assert after["allow_pubmed_deepen"] is False
    assert after["allow_table_deepen"] is True
    assert after["allow_doc_deepen"] is False
    assert after["final_critic_enable"] is False


def test_filter_tool_calls_for_workflow_respects_source_switches():
    workflow = {
        "allow_pubmed_deepen": False,
        "allow_table_deepen": True,
        "allow_doc_deepen": False,
    }
    plan = [
        {"tool": "pubmed_fetch", "params": {"pmids": ["12345678"]}},
        {"tool": "table_rows", "params": {"table": "Engineered_sup_tRNA", "page": 1, "page_size": 1}},
        {"tool": "repo_search", "params": {"query": "AIYingying"}},
    ]

    filtered = routes._filter_tool_calls_for_workflow(plan, workflow, 6)

    assert filtered == [
        {"tool": "table_rows", "params": {"table": "Engineered_sup_tRNA", "page": 1, "page_size": 1}}
    ]


def test_filter_tool_calls_normalizes_and_dedupes_table_tools():
    workflow = {
        "allow_pubmed_deepen": True,
        "allow_table_deepen": True,
        "allow_doc_deepen": True,
    }
    plan = [
        {"tool": "table_info", "params": {"table": "Engineered sup-tRNA"}},
        {"tool": "table_info", "params": {"table": "engineered_sup_trna"}},
        {"tool": "table_info", "params": {}},
        {"tool": "table_rows", "params": {"table": "", "page": 1, "page_size": 1}},
    ]

    filtered = routes._filter_tool_calls_for_workflow(plan, workflow, 6)

    assert filtered == [
        {"tool": "table_info", "params": {"table": "Engineered_sup_tRNA"}},
    ]


def test_apply_request_workflow_overrides_disables_deep_review():
    workflow = {
        "workflow_enable": True,
        "max_retrieval_rounds": 3,
        "retrieval_judge_enable": True,
        "final_critic_enable": True,
    }

    effective = routes._apply_request_workflow_overrides(workflow, {"deep_review": False})

    assert effective["request_deep_review"] is False
    assert effective["max_retrieval_rounds"] == 1
    assert effective["retrieval_judge_enable"] is False
    assert effective["final_critic_enable"] is False


def test_orchestrate_retrieval_runs_multiple_rounds(app_ctx: Flask, monkeypatch: pytest.MonkeyPatch):
    judge_results = iter(
        [
            {
                "enough": False,
                "coverage_score": 0.4,
                "missing_aspects": ["Need row-level PMID evidence"],
                "tool_calls": [{"tool": "table_rows", "params": {"table": "Engineered_sup_tRNA", "page": 1, "page_size": 1}}],
                "stop": False,
                "stop_reason": "",
            },
            {
                "enough": True,
                "coverage_score": 0.95,
                "missing_aspects": [],
                "tool_calls": [],
                "stop": False,
                "stop_reason": "",
            },
        ]
    )

    monkeypatch.setattr(
        routes,
        "_plan_tools",
        lambda question, rag_context, max_steps: [{"tool": "docs_search", "params": {"keyword": "engineered", "limit": 1}}],
    )
    monkeypatch.setattr(routes, "_augment_plan_with_heuristics", lambda plan, question, max_steps: list(plan))
    monkeypatch.setattr(routes, "_judge_retrieval", lambda *args, **kwargs: next(judge_results))
    monkeypatch.setattr(routes, "_evidence_gate", lambda *args, **kwargs: ("", ""))

    def fake_execute_tool(name: str, params: dict):
        if name == "docs_search":
            return {"hits": [{"filename": "0-ENSURE-Overview.md", "snippet": "overview"}], "query": params.get("keyword")}
        if name == "table_rows":
            return {
                "table": "Engineered_sup_tRNA",
                "total": 1,
                "rows": [{"PMID": "12345678", "Gene": "CFTR"}],
            }
        return {"ok": True}

    monkeypatch.setattr(routes, "_execute_tool", fake_execute_tool)

    result = routes._orchestrate_retrieval(
        "Need PMID-backed evidence",
        "RAG context",
        "RAG evidence",
        {
            "workflow_enable": True,
            "max_retrieval_rounds": 2,
            "max_tool_steps_per_round": 4,
            "max_total_tool_steps": 12,
            "retrieval_judge_enable": True,
            "retrieval_judge_threshold": 0.8,
            "stop_on_no_new_evidence": True,
            "stop_on_repeated_plan": True,
            "allow_pubmed_deepen": True,
            "allow_table_deepen": True,
            "allow_doc_deepen": True,
            "final_critic_enable": True,
        },
    )

    assert result["stop_reason"] == "max_rounds_reached"
    assert [item["tool"] for item in result["tool_trace"]] == ["docs_search", "table_rows"]
    assert "Tool `table_rows`" in result["evidence"]


def test_orchestrate_retrieval_falls_back_after_invalid_judge_table_plan(app_ctx: Flask, monkeypatch: pytest.MonkeyPatch):
    judge_results = iter(
        [
            {
                "enough": False,
                "coverage_score": 0.2,
                "missing_aspects": ["table descriptions", "table schemas"],
                "tool_calls": [
                    {"tool": "table_info", "params": {}},
                    {"tool": "table_info", "params": {"table": ""}},
                    {"tool": "table_info", "params": {"dataset": "unknown"}},
                ],
                "stop": False,
                "stop_reason": "",
            },
            {
                "enough": True,
                "coverage_score": 0.95,
                "missing_aspects": [],
                "tool_calls": [],
                "stop": False,
                "stop_reason": "",
            },
        ]
    )
    plans = iter(
        [
            [{"tool": "tables_list", "params": {}}],
            [{"tool": "table_rows", "params": {"table": "Engineered sup-tRNA", "page": 1, "page_size": 1}}],
        ]
    )

    monkeypatch.setattr(routes, "_plan_tools", lambda question, rag_context, max_steps: next(plans))
    monkeypatch.setattr(routes, "_augment_plan_with_heuristics", lambda plan, question, max_steps: list(plan))
    monkeypatch.setattr(routes, "_judge_retrieval", lambda *args, **kwargs: next(judge_results))
    monkeypatch.setattr(routes, "_evidence_gate", lambda *args, **kwargs: ("", ""))

    executed = []

    def fake_execute_tool(name: str, params: dict):
        executed.append((name, dict(params)))
        if name == "tables_list":
            return {"tables": routes.EXPORT_TABLES}
        if name == "table_rows":
            return {
                "table": "Engineered_sup_tRNA",
                "total": 1,
                "rows": [{"PMID": "12345678", "Gene": "CFTR"}],
            }
        if name == "table_info":
            return {"error": "unexpected table_info execution"}
        return {"ok": True}

    monkeypatch.setattr(routes, "_execute_tool", fake_execute_tool)

    result = routes._orchestrate_retrieval(
        "Tell me more about ENSURE data tables",
        "RAG context",
        "RAG evidence",
        {
            "workflow_enable": True,
            "max_retrieval_rounds": 2,
            "max_tool_steps_per_round": 4,
            "max_total_tool_steps": 12,
            "retrieval_judge_enable": True,
            "retrieval_judge_threshold": 0.8,
            "stop_on_no_new_evidence": True,
            "stop_on_repeated_plan": True,
            "allow_pubmed_deepen": True,
            "allow_table_deepen": True,
            "allow_doc_deepen": True,
            "final_critic_enable": True,
        },
    )

    assert [item["tool"] for item in result["tool_trace"]] == ["tables_list", "table_rows"]
    assert [name for name, _ in executed] == ["tables_list", "table_rows"]
    assert executed[1][1]["table"] == "Engineered_sup_tRNA"


def test_chat_message_streams_final_answer_only(monkeypatch: pytest.MonkeyPatch):
    app = build_test_app(register_routes=True)
    generated_contexts = []
    judge_results = iter(
        [
            {
                "enough": False,
                "coverage_score": 0.4,
                "missing_aspects": ["Need row-level PMID evidence"],
                "tool_calls": [{"tool": "table_rows", "params": {"table": "Engineered_sup_tRNA", "page": 1, "page_size": 1}}],
                "stop": False,
                "stop_reason": "",
            },
            {
                "enough": True,
                "coverage_score": 0.95,
                "missing_aspects": [],
                "tool_calls": [],
                "stop": False,
                "stop_reason": "",
            },
        ]
    )

    monkeypatch.setattr(
        routes,
        "_get_llm_runtime",
        lambda requested_model="": {
            "provider": "deepseek",
            "model": requested_model or "deepseek-chat",
            "timeout": 120,
            "system_prompt": "You are Yingying.",
            "max_messages": 20,
            "model_options": ["deepseek-chat"],
            "ollama_models": [],
            "deepseek_models": ["deepseek-chat"],
        },
    )
    monkeypatch.setattr(routes, "_get_ai_workflow_config", lambda: {
        "workflow_enable": True,
        "conversation_router_enable": True,
        "conversation_router_model": "",
        "conversation_router_timeout": 15,
        "router_confidence_threshold": 0.7,
        "max_retrieval_rounds": 2,
        "max_tool_steps_per_round": 4,
        "max_total_tool_steps": 12,
        "retrieval_judge_enable": True,
        "retrieval_judge_model": "",
        "retrieval_judge_threshold": 0.8,
        "stop_on_no_new_evidence": True,
        "stop_on_repeated_plan": True,
        "allow_pubmed_deepen": True,
        "allow_table_deepen": True,
        "allow_doc_deepen": True,
        "final_critic_enable": True,
    })
    monkeypatch.setattr(
        routes,
        "_route_conversation_request",
        lambda runtime, model, session_messages, question, workflow, intent, force_evidence: {
            "route": "knowledge_retrieval",
            "confidence": 1.0,
            "reason": "test",
            "transform_type": "none",
            "target_message_role": "",
            "target_message_offset": 0,
            "target_language": "",
            "clarification_question": "",
        },
    )
    monkeypatch.setattr(routes, "_rag_retrieve", lambda question: ("RAG context", "RAG evidence"))
    monkeypatch.setattr(
        routes,
        "_plan_tools",
        lambda question, rag_context, max_steps: [{"tool": "docs_search", "params": {"keyword": "engineered", "limit": 1}}],
    )
    monkeypatch.setattr(routes, "_augment_plan_with_heuristics", lambda plan, question, max_steps: list(plan))
    monkeypatch.setattr(routes, "_judge_retrieval", lambda *args, **kwargs: next(judge_results))
    monkeypatch.setattr(routes, "_evidence_gate", lambda *args, **kwargs: ("", ""))
    def fake_generate_answer(runtime, system_prompt, session_messages, evidence_context, question, style_prompt=""):
        generated_contexts.append(evidence_context)
        return "Final answer from reviewed evidence [S2]."

    monkeypatch.setattr(routes, "_generate_answer", fake_generate_answer)
    monkeypatch.setattr(routes, "_critique_answer", lambda *args, **kwargs: {"verdict": "ok", "tool_calls": [], "revised_answer": ""})
    monkeypatch.setattr(
        routes,
        "_llm_stream",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("reviewed final answer must not be regenerated")),
    )

    def fake_execute_tool(name: str, params: dict):
        if name == "docs_search":
            return {"hits": [{"filename": "0-ENSURE-Overview.md", "snippet": "overview"}], "query": params.get("keyword")}
        if name == "table_rows":
            return {
                "table": "Engineered_sup_tRNA",
                "total": 1,
                "rows": [{"PMID": "12345678", "Gene": "CFTR"}],
            }
        return {"ok": True}

    monkeypatch.setattr(routes, "_execute_tool", fake_execute_tool)

    with app.test_client() as client:
        open_response = client.get("/chat/api/open")
        chat_id = open_response.get_json()["data"]
        response = client.post(
            f"/chat/api/chat_message/{chat_id}",
            json={"message": "Need final-only streaming", "stream": True},
        )
        payload = response.data.decode("utf-8")

    events = []
    for line in payload.splitlines():
        if not line.startswith("data: "):
            continue
        body = line[6:]
        if body == "[DONE]":
            continue
        events.append(json.loads(body))

    content_events = [event for event in events if event.get("type") == "content"]
    judge_events = [event for event in events if event.get("type") == "judge"]
    draft_events = [event for event in events if event.get("type") == "draft_preview"]
    evidence_events = [event for event in events if event.get("type") == "evidence"]
    assert "".join(event.get("content", "") for event in content_events) == "Final answer from reviewed evidence [S2]."

    deliver_index = next(i for i, event in enumerate(events) if event.get("status") == "Delivering final answer")
    first_content_index = next(i for i, event in enumerate(events) if event.get("type") == "content")
    assert first_content_index > deliver_index
    statuses = [event.get("status") for event in events if event.get("type") == "status"]
    assert "Generating reviewed answer" in statuses
    assert "Reviewing answer" in statuses
    assert any(event.get("type") == "tool" for event in events)
    assert judge_events
    assert draft_events
    assert draft_events[0].get("content") == "Final answer from reviewed evidence [S2]."
    assert judge_events[0].get("verdict") == "continue"
    assert len(generated_contexts) == 1
    assert "Structured source ledger" in generated_contexts[0]
    assert "[S1]" in generated_contexts[0]
    assert evidence_events and evidence_events[-1].get("sources")
    assert all(source.get("source_id", "").startswith("S") for source in evidence_events[-1]["sources"])
    assert any(source.get("source_type") == "table_row" for source in evidence_events[-1]["sources"])


def test_finalizer_does_not_regenerate_after_critic_for_pubmed_evidence(
    monkeypatch: pytest.MonkeyPatch,
):
    app = build_test_app(register_routes=True)
    calls = []

    def fake_generate_answer(*args, **kwargs):
        calls.append((args, kwargs))
        return "The reviewed answer cites the collected literature."

    monkeypatch.setattr(routes, "_generate_answer", fake_generate_answer)
    monkeypatch.setattr(
        routes,
        "_critique_answer",
        lambda *args, **kwargs: {
            "verdict": "ok",
            "tool_calls": [],
            "revised_answer": "",
        },
    )

    workflow = {
        "final_critic_enable": True,
        "max_total_tool_steps": 12,
        "max_tool_steps_per_round": 4,
        "allow_pubmed_deepen": True,
        "allow_table_deepen": True,
        "allow_doc_deepen": True,
    }
    with app.app_context():
        finalizer = routes._finalize_answer(
            {"provider": "xiaomi", "model": "mimo-v2.5-pro"},
            "system",
            [],
            "question",
            "style",
            "context",
            "",
            {},
            {"pubmed_abstracts": 1},
            [],
            workflow,
        )
        events = []
        while True:
            try:
                events.append(next(finalizer))
            except StopIteration as stop:
                result = stop.value
                break

    assert len(calls) == 1
    assert result["answer"] == "The reviewed answer cites the collected literature."
    assert not any(event.get("status") == "Integrating literature evidence" for event in events)


def test_finalizer_rejects_tool_markup_from_critic_revision(monkeypatch: pytest.MonkeyPatch):
    app = build_test_app()
    monkeypatch.setattr(routes, "_generate_answer", lambda *args, **kwargs: "Safe evidence-based answer.")
    monkeypatch.setattr(
        routes,
        "_critique_answer",
        lambda *args, **kwargs: {
            "verdict": "revise",
            "tool_calls": [],
            "revised_answer": "<function=query_db><parameter=sql>SELECT * FROM hidden",
        },
    )

    with app.app_context():
        finalizer = routes._finalize_answer(
            {"provider": "xiaomi", "model": "mimo-v2.5-pro"},
            "system",
            [],
            "question",
            "style",
            "context",
            "",
            {},
            {},
            [],
            {
                "final_critic_enable": True,
                "max_total_tool_steps": 4,
                "max_tool_steps_per_round": 2,
                "allow_pubmed_deepen": True,
                "allow_table_deepen": True,
                "allow_doc_deepen": True,
            },
        )
        while True:
            try:
                next(finalizer)
            except StopIteration as stop:
                result = stop.value
                break

    assert result["answer"] == "Safe evidence-based answer."
    assert "<function" not in result["answer"]


def test_ensure_id_extraction_and_plan_prioritize_every_exact_record(
    monkeypatch: pytest.MonkeyPatch,
):
    question = "比较 ENSURE_ID 1206 与 1211，并列出 ENSURE-0042 的证据。"

    assert routes._extract_ensure_ids(question) == [
        "ENSURE-1206",
        "ENSURE-1211",
        "ENSURE-42",
    ]

    plan = routes._augment_plan_with_heuristics(
        [{"tool": "docs_search", "params": {"keyword": "unrelated"}}],
        question,
        4,
    )
    assert [item["tool"] for item in plan[:3]] == [
        "ensure_lookup",
        "ensure_lookup",
        "ensure_lookup",
    ]
    assert [item["params"]["ensure_id"] for item in plan[:3]] == [
        "ENSURE-1206",
        "ENSURE-1211",
        "ENSURE-42",
    ]
    assert {"1206", "ENSURE1206", "ENSURE-1206", "ENSURE_1206"} <= set(
        routes._expand_ensure_ids(["ENSURE_ID 1206"])
    )

    monkeypatch.setattr(
        routes,
        "_get_tool_router_config",
        lambda: (True, 4, "", 15, 5000),
    )
    monkeypatch.setattr(
        routes,
        "_llm_once",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("exact ENSURE IDs must bypass the model planner")
        ),
    )
    assert routes._plan_tools(question, "", 4)[:3] == plan[:3]

    routed = routes._route_conversation_request(
        {"model": "mimo-v2.5-pro"},
        "mimo-v2.5-pro",
        [],
        question,
        {"conversation_router_enable": True},
        "retrieval",
        True,
    )
    assert routed["route"] == "knowledge_retrieval"
    assert routed["reason"] == "exact_ensure_id_retrieval"
    assert not routes._looks_like_repo_question("Compare the reporter fields")
    assert routes._looks_like_repo_question("Inspect the repo implementation")


def test_critic_disables_provider_thinking(monkeypatch: pytest.MonkeyPatch):
    captured = {}

    def fake_llm_once(runtime, messages, model="", timeout=None):
        captured.update(runtime)
        return '{"verdict":"ok","tool_calls":[],"revised_answer":""}'

    monkeypatch.setattr(routes, "_llm_once", fake_llm_once)

    result = routes._critique_answer(
        {"provider": "xiaomi", "thinking_enabled": True},
        "question",
        "answer",
        "evidence",
    )

    assert result["verdict"] == "ok"
    assert captured["thinking_enabled"] is False


def test_structured_sources_prioritize_exact_records_and_split_multi_pmids():
    tool_cache = {
        "docs_search:first": {
            "hits": [{"filename": "0-ENSURE-Overview.md", "snippet": "Database overview"}],
        },
        "table_rows:second": {
            "table": "Engineered_sup_tRNA",
            "rows": [{
                "ENSURE_ID": "ENSURE 0042",
                "PMID": "12345678; 23456789 / invalid",
                "DOI": "https://doi.org/10.1000/example",
                "PTC gene": "CFTR",
            }],
        },
    }

    sources = routes._build_structured_sources(
        "1. A generic RAG summary without a resolvable record.",
        tool_cache,
        [],
    )

    assert [source["source_type"] for source in sources[:2]] == ["table_row", "table_row"]
    assert [source["PMID"] for source in sources[:2]] == ["12345678", "23456789"]
    assert all(source["url"] == "/expanded/ENSURE%200042" for source in sources[:2])
    assert all(";" not in source["PMID"] for source in sources)
    assert [source["source_id"] for source in sources] == [f"S{index}" for index in range(1, len(sources) + 1)]
    document = next(source for source in sources if source["source_type"] == "document")
    assert document["url"] == "/help.html?file=0-ENSURE-Overview.md"


def test_engineered_source_excerpt_prioritizes_answer_fields():
    row = {
        "Index": 1,
        "Related_disease": "Reporter assay",
        "PTC_gene": "mCherry-STOP-GFP",
        "PTC_codon": "UAG",
        "aa_and_anticodon_of_sup-tRNA": "Leu(CUA)",
        "Species_source_of_origin_tRNA": "Homo sapiens",
        "Reaction_system": "HEK293T screen",
        "Reading_through_efficiency": "56%",
        "ENSURE_ID": "1206",
        "PMID": "41261131",
    }

    source = routes._table_row_sources("Engineered_sup_tRNA", row)[0]

    for expected in (
        "ENSURE_ID: 1206",
        "PMID: 41261131",
        "PTC_gene: mCherry-STOP-GFP",
        "PTC_codon: UAG",
        "aa_and_anticodon_of_sup-tRNA: Leu(CUA)",
        "Species_source_of_origin_tRNA: Homo sapiens",
    ):
        assert expected in source["excerpt"]


def test_table_sources_have_internal_query_links_and_safe_external_urls():
    table_sources = routes._table_row_sources(
        "coding_variation_cancer",
        {"ID": 42, "PMID": "12345678,23456789", "Gene Name": "CFTR"},
    )

    assert [source["PMID"] for source in table_sources] == ["12345678", "23456789"]
    assert all(source["url"].startswith("/CodingVariationDisease?") for source in table_sources)
    assert all("table=coding_variation_cancer" in source["url"] for source in table_sources)
    assert all("search_column=ID" in source["url"] for source in table_sources)
    assert all("search_text=42" in source["url"] for source in table_sources)

    doi_source = routes._new_structured_source(
        "pubmed_article",
        doi="https://doi.org/10.1000/a value",
    )
    assert doi_source["url"] == "https://doi.org/10.1000/a%20value"


def test_structured_source_model_context_has_strict_budget():
    sources = [
        {
            "source_id": f"S{index}",
            "source_type": "table_row",
            "table": "Engineered_sup_tRNA",
            "record_pk": str(index),
            "ENSURE_ID": "",
            "PMID": str(10000000 + index),
            "DOI": "",
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{10000000 + index}/",
            "excerpt": "x" * 900,
        }
        for index in range(1, 31)
    ]

    ledger = routes._structured_sources_context(sources)

    assert len(sources) == 30
    assert len(ledger) <= routes._STRUCTURED_SOURCE_CONTEXT_MAX_CHARS
    ledger_source_count = ledger.count("\n[S")
    assert 12 <= ledger_source_count <= routes._STRUCTURED_SOURCE_CONTEXT_MAX_SOURCES
    assert f"[S{ledger_source_count}]" in ledger
    assert f"[S{ledger_source_count + 1}]" not in ledger


def test_structured_source_builder_caps_default_sse_payload():
    tool_cache = {
        "docs_search:many": {
            "hits": [
                {"filename": f"source-{index}.md", "snippet": f"Evidence {index}"}
                for index in range(40)
            ]
        }
    }

    sources = routes._build_structured_sources("", tool_cache, [])

    assert len(sources) == routes._STRUCTURED_SOURCE_CONTEXT_MAX_SOURCES
    assert sources[-1]["source_id"] == f"S{routes._STRUCTURED_SOURCE_CONTEXT_MAX_SOURCES}"


def test_source_citation_validation_removes_unknown_ids_and_enforces_one_real_source():
    sources = [{"source_id": "S1"}, {"source_id": "S2"}]

    cleaned, cited, removed = routes._validate_answer_source_citations(
        "Supported [S2], invented [S99].",
        sources,
        require_citation=True,
    )
    assert cleaned == "Supported [S2], invented."
    assert cited == ["S2"]
    assert removed == ["S99"]

    enforced, cited, removed = routes._validate_answer_source_citations(
        "A factual answer without an inline source.",
        sources,
        require_citation=True,
    )
    assert enforced.endswith("[S1]")
    assert cited == ["S1"]
    assert removed == []


def test_chat_message_deep_review_false_skips_judge_and_final_critic(monkeypatch: pytest.MonkeyPatch):
    app = build_test_app(register_routes=True)

    monkeypatch.setattr(
        routes,
        "_get_llm_runtime",
        lambda requested_model="": {
            "provider": "deepseek",
            "model": requested_model or "deepseek-chat",
            "timeout": 120,
            "system_prompt": "You are Yingying.",
            "max_messages": 20,
            "model_options": ["deepseek-chat"],
            "ollama_models": [],
            "deepseek_models": ["deepseek-chat"],
        },
    )
    monkeypatch.setattr(routes, "_get_ai_workflow_config", lambda: {
        "workflow_enable": True,
        "conversation_router_enable": True,
        "conversation_router_model": "",
        "conversation_router_timeout": 15,
        "router_confidence_threshold": 0.7,
        "max_retrieval_rounds": 2,
        "max_tool_steps_per_round": 4,
        "max_total_tool_steps": 12,
        "retrieval_judge_enable": True,
        "retrieval_judge_model": "",
        "retrieval_judge_threshold": 0.8,
        "stop_on_no_new_evidence": True,
        "stop_on_repeated_plan": True,
        "allow_pubmed_deepen": True,
        "allow_table_deepen": True,
        "allow_doc_deepen": True,
        "final_critic_enable": True,
    })
    monkeypatch.setattr(
        routes,
        "_route_conversation_request",
        lambda runtime, model, session_messages, question, workflow, intent, force_evidence: {
            "route": "knowledge_retrieval",
            "confidence": 1.0,
            "reason": "test",
            "transform_type": "none",
            "target_message_role": "",
            "target_message_offset": 0,
            "target_language": "",
            "clarification_question": "",
        },
    )
    monkeypatch.setattr(routes, "_rag_retrieve", lambda question: ("RAG context", "RAG evidence"))
    monkeypatch.setattr(
        routes,
        "_plan_tools",
        lambda question, rag_context, max_steps: [{"tool": "docs_search", "params": {"keyword": "engineered", "limit": 1}}],
    )
    monkeypatch.setattr(routes, "_augment_plan_with_heuristics", lambda plan, question, max_steps: list(plan))
    monkeypatch.setattr(routes, "_evidence_gate", lambda *args, **kwargs: ("", ""))
    monkeypatch.setattr(
        routes,
        "_judge_retrieval",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("judge should be skipped when deep review is disabled")),
    )
    monkeypatch.setattr(
        routes,
        "_critique_answer",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("final critic should be skipped when deep review is disabled")),
    )
    monkeypatch.setattr(
        routes,
        "_llm_stream",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("the finalized answer must be replayed, not generated as a second stream")
        ),
    )
    monkeypatch.setattr(
        routes,
        "_generate_answer",
        lambda *args, **kwargs: "Fast answer [S1].",
    )

    def fake_execute_tool(name: str, params: dict):
        if name == "docs_search":
            return {"hits": [{"filename": "0-ENSURE-Overview.md", "snippet": "overview"}], "query": params.get("keyword")}
        return {"ok": True}

    monkeypatch.setattr(routes, "_execute_tool", fake_execute_tool)

    with app.test_client() as client:
        open_response = client.get("/chat/api/open")
        chat_id = open_response.get_json()["data"]
        response = client.post(
            f"/chat/api/chat_message/{chat_id}",
            json={"message": "Need a faster answer", "stream": True, "deep_review": False},
        )
        payload = response.data.decode("utf-8")

    events = []
    for line in payload.splitlines():
        if not line.startswith("data: "):
            continue
        body = line[6:]
        if body == "[DONE]":
            continue
        events.append(json.loads(body))

    statuses = [event.get("status") for event in events if event.get("type") == "status"]
    content = "".join(event.get("content", "") for event in events if event.get("type") == "content")
    judge_events = [event for event in events if event.get("type") == "judge"]

    assert "Fast response mode" in statuses
    assert "Generating final answer" in statuses
    assert "Reviewing answer" not in statuses
    assert not judge_events
    assert content == "Fast answer [S1]."


def test_route_conversation_request_uses_ai_router_for_history_transform(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        routes,
        "_llm_once",
        lambda runtime, messages, model="", timeout=None: json.dumps(
            {
                "route": "history_transform",
                "confidence": 0.96,
                "reason": "The user asked to translate the previous assistant answer.",
                "transform_type": "translate",
                "target_message_role": "assistant",
                "target_message_offset": 1,
                "target_language": "zh",
                "clarification_question": "",
            },
            ensure_ascii=False,
        ),
    )

    decision = routes._route_conversation_request(
        {
            "provider": "deepseek",
            "model": "deepseek-chat",
            "timeout": 120,
            "system_prompt": "You are Yingying.",
            "max_messages": 20,
            "model_options": ["deepseek-chat"],
            "ollama_models": [],
            "deepseek_models": ["deepseek-chat"],
        },
        "deepseek-chat",
        [
            {"role": "user", "content": "What is ENSURE?"},
            {"role": "assistant", "content": "ENSURE is a tRNA-focused database and research platform."},
            {"role": "user", "content": "把上一次回答翻译成中文"},
        ],
        "把上一次回答翻译成中文",
        {
            "conversation_router_enable": True,
            "conversation_router_model": "",
            "conversation_router_timeout": 15,
            "router_confidence_threshold": 0.7,
        },
        "general",
        False,
    )

    assert decision["route"] == "history_transform"
    assert decision["transform_type"] == "translate"
    assert decision["target_message_role"] == "assistant"
    assert decision["target_message_offset"] == 1
    assert decision["target_language"] == "zh"
    assert decision["source_text"] == "ENSURE is a tRNA-focused database and research platform."


def test_translation_followup_bypasses_retrieval_via_ai_router(monkeypatch: pytest.MonkeyPatch):
    app = build_test_app(register_routes=True)
    calls = {"rag": 0, "planner": 0, "judge": 0}

    monkeypatch.setattr(
        routes,
        "_get_llm_runtime",
        lambda requested_model="": {
            "provider": "deepseek",
            "model": requested_model or "deepseek-chat",
            "timeout": 120,
            "system_prompt": "You are Yingying.",
            "max_messages": 20,
            "model_options": ["deepseek-chat"],
            "ollama_models": [],
            "deepseek_models": ["deepseek-chat"],
        },
    )
    monkeypatch.setattr(routes, "_get_ai_workflow_config", lambda: {
        "workflow_enable": True,
        "conversation_router_enable": True,
        "conversation_router_model": "",
        "conversation_router_timeout": 15,
        "router_confidence_threshold": 0.7,
        "max_retrieval_rounds": 2,
        "max_tool_steps_per_round": 4,
        "max_total_tool_steps": 12,
        "retrieval_judge_enable": True,
        "retrieval_judge_model": "",
        "retrieval_judge_threshold": 0.8,
        "stop_on_no_new_evidence": True,
        "stop_on_repeated_plan": True,
        "allow_pubmed_deepen": True,
        "allow_table_deepen": True,
        "allow_doc_deepen": True,
        "final_critic_enable": True,
    })
    llm_outputs = iter(
        [
            json.dumps(
                {
                    "route": "history_transform",
                    "confidence": 0.96,
                    "reason": "The user asked to translate the previous assistant answer.",
                    "transform_type": "translate",
                    "target_message_role": "assistant",
                    "target_message_offset": 1,
                    "target_language": "zh",
                    "clarification_question": "",
                },
                ensure_ascii=False,
            ),
            "ENSURE 是一个专注于 tRNA 的数据库和研究平台。",
        ]
    )
    monkeypatch.setattr(routes, "_llm_once", lambda runtime, messages, model="", timeout=None: next(llm_outputs))

    def fake_rag(question):
        calls["rag"] += 1
        return ("unexpected", "unexpected")

    def fake_plan(question, rag_context, max_steps):
        calls["planner"] += 1
        return []

    def fake_judge(*args, **kwargs):
        calls["judge"] += 1
        return {"enough": True, "coverage_score": 1.0, "missing_aspects": [], "tool_calls": [], "stop": False, "stop_reason": ""}

    monkeypatch.setattr(routes, "_rag_retrieve", fake_rag)
    monkeypatch.setattr(routes, "_plan_tools", fake_plan)
    monkeypatch.setattr(routes, "_judge_retrieval", fake_judge)

    with app.test_client() as client:
        open_resp = client.get("/chat/api/open")
        chat_id = open_resp.get_json()["data"]
        response = client.post(
            f"/chat/api/chat_message/{chat_id}",
            json={
                "message": "把上一次回答翻译成中文",
                "stream": True,
                "history": [
                    {"role": "user", "content": "What is ENSURE?"},
                    {"role": "assistant", "content": "ENSURE is a tRNA-focused database and research platform."},
                ],
            },
        )
        payload = response.data.decode("utf-8")

    events = []
    for line in payload.splitlines():
        if not line.startswith("data: "):
            continue
        body = line[6:]
        if body == "[DONE]":
            continue
        events.append(json.loads(body))

    statuses = [event.get("status") for event in events if event.get("type") == "status"]
    content = "".join(event.get("content", "") for event in events if event.get("type") == "content")
    evidence = [event.get("content", "") for event in events if event.get("type") == "evidence"]
    evidence = [event.get("content", "") for event in events if event.get("type") == "evidence"]
    evidence = [event.get("content", "") for event in events if event.get("type") == "evidence"]
    evidence = [event.get("content", "") for event in events if event.get("type") == "evidence"]
    evidence = [event.get("content", "") for event in events if event.get("type") == "evidence"]
    evidence = [event.get("content", "") for event in events if event.get("type") == "evidence"]
    evidence = [event.get("content", "") for event in events if event.get("type") == "evidence"]

    assert calls == {"rag": 0, "planner": 0, "judge": 0}
    assert statuses == ["Analyzing question", "Routing request", "Rewriting previous answer", "Delivering final answer"]
    assert content == "ENSURE 是一个专注于 tRNA 的数据库和研究平台。"
    assert evidence and "Route: history_transform" in evidence[-1]
    assert not any(event.get("type") == "tool" for event in events)


def test_summary_followup_bypasses_retrieval_via_ai_router(monkeypatch: pytest.MonkeyPatch):
    app = build_test_app(register_routes=True)
    calls = {"rag": 0, "planner": 0, "judge": 0}

    monkeypatch.setattr(
        routes,
        "_get_llm_runtime",
        lambda requested_model="": {
            "provider": "deepseek",
            "model": requested_model or "deepseek-chat",
            "timeout": 120,
            "system_prompt": "You are Yingying.",
            "max_messages": 20,
            "model_options": ["deepseek-chat"],
            "ollama_models": [],
            "deepseek_models": ["deepseek-chat"],
        },
    )
    monkeypatch.setattr(routes, "_get_ai_workflow_config", lambda: {
        "workflow_enable": True,
        "conversation_router_enable": True,
        "conversation_router_model": "",
        "conversation_router_timeout": 15,
        "router_confidence_threshold": 0.7,
        "max_retrieval_rounds": 2,
        "max_tool_steps_per_round": 4,
        "max_total_tool_steps": 12,
        "retrieval_judge_enable": True,
        "retrieval_judge_model": "",
        "retrieval_judge_threshold": 0.8,
        "stop_on_no_new_evidence": True,
        "stop_on_repeated_plan": True,
        "allow_pubmed_deepen": True,
        "allow_table_deepen": True,
        "allow_doc_deepen": True,
        "final_critic_enable": True,
    })
    llm_outputs = iter(
        [
            json.dumps(
                {
                    "route": "history_transform",
                    "confidence": 0.94,
                    "reason": "The user wants a summary of the previous assistant answer.",
                    "transform_type": "summarize",
                    "target_message_role": "assistant",
                    "target_message_offset": 1,
                    "target_language": "zh",
                    "clarification_question": "",
                },
                ensure_ascii=False,
            ),
            "ENSURE 是一个聚焦 tRNA 的数据库与研究平台，整合了相关数据、文档与分析入口。",
        ]
    )
    monkeypatch.setattr(routes, "_llm_once", lambda runtime, messages, model="", timeout=None: next(llm_outputs))

    def fake_rag(question):
        calls["rag"] += 1
        return ("unexpected", "unexpected")

    def fake_plan(question, rag_context, max_steps):
        calls["planner"] += 1
        return []

    def fake_judge(*args, **kwargs):
        calls["judge"] += 1
        return {"enough": True, "coverage_score": 1.0, "missing_aspects": [], "tool_calls": [], "stop": False, "stop_reason": ""}

    monkeypatch.setattr(routes, "_rag_retrieve", fake_rag)
    monkeypatch.setattr(routes, "_plan_tools", fake_plan)
    monkeypatch.setattr(routes, "_judge_retrieval", fake_judge)

    with app.test_client() as client:
        open_resp = client.get("/chat/api/open")
        chat_id = open_resp.get_json()["data"]
        response = client.post(
            f"/chat/api/chat_message/{chat_id}",
            json={
                "message": "把上一次回答总结成一句话",
                "stream": True,
                "history": [
                    {"role": "user", "content": "What is ENSURE?"},
                    {"role": "assistant", "content": "ENSURE is a tRNA-focused database and research platform that integrates curated datasets and supporting docs."},
                ],
            },
        )
        payload = response.data.decode("utf-8")

    events = []
    for line in payload.splitlines():
        if not line.startswith("data: "):
            continue
        body = line[6:]
        if body == "[DONE]":
            continue
        events.append(json.loads(body))

    statuses = [event.get("status") for event in events if event.get("type") == "status"]
    content = "".join(event.get("content", "") for event in events if event.get("type") == "content")
    evidence = [event.get("content", "") for event in events if event.get("type") == "evidence"]

    assert calls == {"rag": 0, "planner": 0, "judge": 0}
    assert statuses == ["Analyzing question", "Routing request", "Rewriting previous answer", "Delivering final answer"]
    assert content == "ENSURE 是一个聚焦 tRNA 的数据库与研究平台，整合了相关数据、文档与分析入口。"
    assert evidence and "Route: history_transform" in evidence[-1]
    assert not any(event.get("type") == "tool" for event in events)


def test_expand_followup_without_new_evidence_bypasses_retrieval_via_ai_router(monkeypatch: pytest.MonkeyPatch):
    app = build_test_app(register_routes=True)
    calls = {"rag": 0, "planner": 0, "judge": 0}

    monkeypatch.setattr(
        routes,
        "_get_llm_runtime",
        lambda requested_model="": {
            "provider": "deepseek",
            "model": requested_model or "deepseek-chat",
            "timeout": 120,
            "system_prompt": "You are Yingying.",
            "max_messages": 20,
            "model_options": ["deepseek-chat"],
            "ollama_models": [],
            "deepseek_models": ["deepseek-chat"],
        },
    )
    monkeypatch.setattr(routes, "_get_ai_workflow_config", lambda: {
        "workflow_enable": True,
        "conversation_router_enable": True,
        "conversation_router_model": "",
        "conversation_router_timeout": 15,
        "router_confidence_threshold": 0.7,
        "max_retrieval_rounds": 2,
        "max_tool_steps_per_round": 4,
        "max_total_tool_steps": 12,
        "retrieval_judge_enable": True,
        "retrieval_judge_model": "",
        "retrieval_judge_threshold": 0.8,
        "stop_on_no_new_evidence": True,
        "stop_on_repeated_plan": True,
        "allow_pubmed_deepen": True,
        "allow_table_deepen": True,
        "allow_doc_deepen": True,
        "final_critic_enable": True,
    })
    llm_outputs = iter(
        [
            json.dumps(
                {
                    "route": "history_transform",
                    "confidence": 0.91,
                    "reason": "The user wants a fuller restatement of the previous assistant answer without new evidence.",
                    "transform_type": "rewrite",
                    "target_message_role": "assistant",
                    "target_message_offset": 1,
                    "target_language": "zh",
                    "clarification_question": "",
                },
                ensure_ascii=False,
            ),
            "ENSURE 不只是一个简单的数据表集合，它还是一个围绕 tRNA 研究组织内容与证据的平台，方便用户同时查看整理后的数据、相关说明文档以及分析入口。",
        ]
    )
    monkeypatch.setattr(routes, "_llm_once", lambda runtime, messages, model="", timeout=None: next(llm_outputs))

    def fake_rag(question):
        calls["rag"] += 1
        return ("unexpected", "unexpected")

    def fake_plan(question, rag_context, max_steps):
        calls["planner"] += 1
        return []

    def fake_judge(*args, **kwargs):
        calls["judge"] += 1
        return {"enough": True, "coverage_score": 1.0, "missing_aspects": [], "tool_calls": [], "stop": False, "stop_reason": ""}

    monkeypatch.setattr(routes, "_rag_retrieve", fake_rag)
    monkeypatch.setattr(routes, "_plan_tools", fake_plan)
    monkeypatch.setattr(routes, "_judge_retrieval", fake_judge)

    with app.test_client() as client:
        open_resp = client.get("/chat/api/open")
        chat_id = open_resp.get_json()["data"]
        response = client.post(
            f"/chat/api/chat_message/{chat_id}",
            json={
                "message": "把上一次回答扩展一点，但不要查新资料",
                "stream": True,
                "history": [
                    {"role": "user", "content": "What is ENSURE?"},
                    {"role": "assistant", "content": "ENSURE is a tRNA-focused database and research platform."},
                ],
            },
        )
        payload = response.data.decode("utf-8")

    events = []
    for line in payload.splitlines():
        if not line.startswith("data: "):
            continue
        body = line[6:]
        if body == "[DONE]":
            continue
        events.append(json.loads(body))

    statuses = [event.get("status") for event in events if event.get("type") == "status"]
    content = "".join(event.get("content", "") for event in events if event.get("type") == "content")
    evidence = [event.get("content", "") for event in events if event.get("type") == "evidence"]

    assert calls == {"rag": 0, "planner": 0, "judge": 0}
    assert statuses == ["Analyzing question", "Routing request", "Rewriting previous answer", "Delivering final answer"]
    assert content == "ENSURE 不只是一个简单的数据表集合，它还是一个围绕 tRNA 研究组织内容与证据的平台，方便用户同时查看整理后的数据、相关说明文档以及分析入口。"
    assert evidence and "Route: history_transform" in evidence[-1]
    assert not any(event.get("type") == "tool" for event in events)


def test_expand_followup_with_new_evidence_uses_retrieval_route(monkeypatch: pytest.MonkeyPatch):
    app = build_test_app(register_routes=True)
    calls = {"rag": 0, "planner": 0, "judge": 0}

    monkeypatch.setattr(
        routes,
        "_get_llm_runtime",
        lambda requested_model="": {
            "provider": "deepseek",
            "model": requested_model or "deepseek-chat",
            "timeout": 120,
            "system_prompt": "You are Yingying.",
            "max_messages": 20,
            "model_options": ["deepseek-chat"],
            "ollama_models": [],
            "deepseek_models": ["deepseek-chat"],
        },
    )
    monkeypatch.setattr(routes, "_get_ai_workflow_config", lambda: {
        "workflow_enable": True,
        "conversation_router_enable": True,
        "conversation_router_model": "",
        "conversation_router_timeout": 15,
        "router_confidence_threshold": 0.7,
        "max_retrieval_rounds": 2,
        "max_tool_steps_per_round": 4,
        "max_total_tool_steps": 12,
        "retrieval_judge_enable": True,
        "retrieval_judge_model": "",
        "retrieval_judge_threshold": 0.8,
        "stop_on_no_new_evidence": True,
        "stop_on_repeated_plan": True,
        "allow_pubmed_deepen": True,
        "allow_table_deepen": True,
        "allow_doc_deepen": True,
        "final_critic_enable": True,
    })
    monkeypatch.setattr(
        routes,
        "_route_conversation_request",
        lambda runtime, model, session_messages, question, workflow, intent, force_evidence: {
            "route": "knowledge_retrieval",
            "confidence": 0.93,
            "reason": "The user requested new examples and PMIDs, so retrieval is required.",
            "transform_type": "none",
            "target_message_role": "",
            "target_message_offset": 0,
            "target_language": "",
            "clarification_question": "",
        },
    )

    def fake_rag(question):
        calls["rag"] += 1
        return ("RAG context", "RAG evidence")

    def fake_plan(question, rag_context, max_steps):
        calls["planner"] += 1
        return [{"tool": "table_rows", "params": {"table": "Engineered_sup_tRNA", "page": 1, "page_size": 1}}]

    def fake_judge(*args, **kwargs):
        calls["judge"] += 1
        return {"enough": True, "coverage_score": 1.0, "missing_aspects": [], "tool_calls": [], "stop": False, "stop_reason": ""}

    monkeypatch.setattr(routes, "_rag_retrieve", fake_rag)
    monkeypatch.setattr(routes, "_plan_tools", fake_plan)
    monkeypatch.setattr(routes, "_augment_plan_with_heuristics", lambda plan, question, max_steps: list(plan))
    monkeypatch.setattr(routes, "_judge_retrieval", fake_judge)
    monkeypatch.setattr(routes, "_evidence_gate", lambda *args, **kwargs: ("", ""))
    monkeypatch.setattr(routes, "_generate_answer", lambda *args, **kwargs: "我补充了一条新的例子，并给出对应的 PMID 作为支持。")
    monkeypatch.setattr(routes, "_critique_answer", lambda *args, **kwargs: {"verdict": "ok", "tool_calls": [], "revised_answer": ""})
    monkeypatch.setattr(
        routes,
        "_execute_tool",
        lambda name, params: {
            "table": "Engineered_sup_tRNA",
            "total": 1,
            "rows": [{"PMID": "12345678", "Gene": "CFTR"}],
        },
    )

    with app.test_client() as client:
        open_resp = client.get("/chat/api/open")
        chat_id = open_resp.get_json()["data"]
        response = client.post(
            f"/chat/api/chat_message/{chat_id}",
            json={
                "message": "在上一次回答基础上再拓展一下，并给我具体例子和 PMID",
                "stream": True,
                "history": [
                    {"role": "user", "content": "What is ENSURE?"},
                    {"role": "assistant", "content": "ENSURE is a tRNA-focused database and research platform."},
                ],
            },
        )
        payload = response.data.decode("utf-8")

    events = []
    for line in payload.splitlines():
        if not line.startswith("data: "):
            continue
        body = line[6:]
        if body == "[DONE]":
            continue
        events.append(json.loads(body))

    statuses = [event.get("status") for event in events if event.get("type") == "status"]
    content = "".join(event.get("content", "") for event in events if event.get("type") == "content")
    evidence = [event.get("content", "") for event in events if event.get("type") == "evidence"]

    assert calls["rag"] == 1
    assert calls["planner"] >= 1
    assert calls["judge"] >= 0
    assert statuses[:3] == ["Analyzing question", "Routing request", "Searching ENSURE data"]
    assert any(event.get("type") == "tool" for event in events)
    assert content == "我补充了一条新的例子，并给出对应的 PMID 作为支持。 [S1]"
    assert evidence


def test_direct_answer_emits_evidence_marker(monkeypatch: pytest.MonkeyPatch):
    app = build_test_app(register_routes=True)

    monkeypatch.setattr(
        routes,
        "_get_llm_runtime",
        lambda requested_model="": {
            "provider": "deepseek",
            "model": requested_model or "deepseek-chat",
            "timeout": 120,
            "system_prompt": "You are Yingying.",
            "max_messages": 20,
            "model_options": ["deepseek-chat"],
            "ollama_models": [],
            "deepseek_models": ["deepseek-chat"],
        },
    )
    monkeypatch.setattr(routes, "_get_ai_workflow_config", lambda: {
        "workflow_enable": True,
        "conversation_router_enable": True,
        "conversation_router_model": "",
        "conversation_router_timeout": 15,
        "router_confidence_threshold": 0.7,
        "max_retrieval_rounds": 2,
        "max_tool_steps_per_round": 4,
        "max_total_tool_steps": 12,
        "retrieval_judge_enable": True,
        "retrieval_judge_model": "",
        "retrieval_judge_threshold": 0.8,
        "stop_on_no_new_evidence": True,
        "stop_on_repeated_plan": True,
        "allow_pubmed_deepen": True,
        "allow_table_deepen": True,
        "allow_doc_deepen": True,
        "final_critic_enable": True,
    })
    monkeypatch.setattr(
        routes,
        "_route_conversation_request",
        lambda runtime, model, session_messages, question, workflow, intent, force_evidence: {
            "route": "direct_answer",
            "confidence": 0.95,
            "reason": "identity question",
            "transform_type": "none",
            "target_message_role": "",
            "target_message_offset": 0,
            "target_language": "",
            "clarification_question": "",
        },
    )
    monkeypatch.setattr(routes, "_llm_once", lambda runtime, messages, model="", timeout=None: "我是荧荧，ENSURE 数据库的 AI 助手。")

    with app.test_client() as client:
        open_resp = client.get("/chat/api/open")
        chat_id = open_resp.get_json()["data"]
        response = client.post(
            f"/chat/api/chat_message/{chat_id}",
            json={"message": "你是谁？", "stream": True},
        )
        payload = response.data.decode("utf-8")

    events = []
    for line in payload.splitlines():
        if not line.startswith("data: "):
            continue
        body = line[6:]
        if body == "[DONE]":
            continue
        events.append(json.loads(body))

    statuses = [event.get("status") for event in events if event.get("type") == "status"]
    evidence = [event.get("content", "") for event in events if event.get("type") == "evidence"]
    content = "".join(event.get("content", "") for event in events if event.get("type") == "content")

    assert statuses == ["Analyzing question", "Routing request", "Drafting final answer", "Delivering final answer"]
    assert content == "我是荧荧，ENSURE 数据库的 AI 助手。"
    assert evidence and "Route: direct_answer" in evidence[-1]


def test_clarify_emits_evidence_marker(monkeypatch: pytest.MonkeyPatch):
    app = build_test_app(register_routes=True)

    monkeypatch.setattr(
        routes,
        "_get_llm_runtime",
        lambda requested_model="": {
            "provider": "deepseek",
            "model": requested_model or "deepseek-chat",
            "timeout": 120,
            "system_prompt": "You are Yingying.",
            "max_messages": 20,
            "model_options": ["deepseek-chat"],
            "ollama_models": [],
            "deepseek_models": ["deepseek-chat"],
        },
    )
    monkeypatch.setattr(routes, "_get_ai_workflow_config", lambda: {
        "workflow_enable": True,
        "conversation_router_enable": True,
        "conversation_router_model": "",
        "conversation_router_timeout": 15,
        "router_confidence_threshold": 0.7,
        "max_retrieval_rounds": 2,
        "max_tool_steps_per_round": 4,
        "max_total_tool_steps": 12,
        "retrieval_judge_enable": True,
        "retrieval_judge_model": "",
        "retrieval_judge_threshold": 0.8,
        "stop_on_no_new_evidence": True,
        "stop_on_repeated_plan": True,
        "allow_pubmed_deepen": True,
        "allow_table_deepen": True,
        "allow_doc_deepen": True,
        "final_critic_enable": True,
    })
    monkeypatch.setattr(
        routes,
        "_route_conversation_request",
        lambda runtime, model, session_messages, question, workflow, intent, force_evidence: {
            "route": "clarify",
            "confidence": 0.82,
            "reason": "ambiguous target",
            "transform_type": "none",
            "target_message_role": "",
            "target_message_offset": 0,
            "target_language": "",
            "clarification_question": "请您明确一下，您是想让我展开上一条回答，还是继续检索新的证据？",
        },
    )

    with app.test_client() as client:
        open_resp = client.get("/chat/api/open")
        chat_id = open_resp.get_json()["data"]
        response = client.post(
            f"/chat/api/chat_message/{chat_id}",
            json={"message": "上面那个再说详细一点", "stream": True},
        )
        payload = response.data.decode("utf-8")

    events = []
    for line in payload.splitlines():
        if not line.startswith("data: "):
            continue
        body = line[6:]
        if body == "[DONE]":
            continue
        events.append(json.loads(body))

    statuses = [event.get("status") for event in events if event.get("type") == "status"]
    evidence = [event.get("content", "") for event in events if event.get("type") == "evidence"]
    content = "".join(event.get("content", "") for event in events if event.get("type") == "content")

    assert statuses == ["Analyzing question", "Routing request", "Asking for clarification", "Delivering final answer"]
    assert content == "请您明确一下，您是想让我展开上一条回答，还是继续检索新的证据？"
    assert evidence and "Route: clarify" in evidence[-1]
