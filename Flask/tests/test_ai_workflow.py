from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
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
    monkeypatch.setattr(routes, "_generate_answer", lambda *args, **kwargs: "Draft answer from reviewed evidence.")
    monkeypatch.setattr(routes, "_critique_answer", lambda *args, **kwargs: {"verdict": "ok", "tool_calls": [], "revised_answer": ""})
    monkeypatch.setattr(
        routes,
        "_llm_stream",
        lambda runtime, messages, model="": iter(
            [
                ("Final ", False),
                ("answer ", False),
                ("from reviewed evidence.", True),
            ]
        ),
    )
    monkeypatch.setattr(
        routes,
        "_stream_text_chunks",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("retrieval branch should not use fake chunking")),
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
        response = client.post(
            "/chat/api/chat_message/test-chat",
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
    assert "".join(event.get("content", "") for event in content_events) == "Final answer from reviewed evidence."

    deliver_index = next(i for i, event in enumerate(events) if event.get("status") == "Delivering final answer")
    first_content_index = next(i for i, event in enumerate(events) if event.get("type") == "content")
    assert first_content_index > deliver_index
    statuses = [event.get("status") for event in events if event.get("type") == "status"]
    assert "Generating reviewed answer" in statuses
    assert "Reviewing answer" in statuses
    assert any(event.get("type") == "tool" for event in events)
    assert judge_events
    assert draft_events
    assert draft_events[0].get("content") == "Draft answer from reviewed evidence."
    assert judge_events[0].get("verdict") == "continue"


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
        lambda runtime, messages, model="": iter(
            [
                ("Fast ", False),
                ("answer.", True),
            ]
        ),
    )
    monkeypatch.setattr(
        routes,
        "_generate_answer",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("fast deep-review-off path should stream directly")),
    )

    def fake_execute_tool(name: str, params: dict):
        if name == "docs_search":
            return {"hits": [{"filename": "0-ENSURE-Overview.md", "snippet": "overview"}], "query": params.get("keyword")}
        return {"ok": True}

    monkeypatch.setattr(routes, "_execute_tool", fake_execute_tool)

    with app.test_client() as client:
        response = client.post(
            "/chat/api/chat_message/test-fast",
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
    assert "Preparing final answer stream" in statuses
    assert "Reviewing answer" not in statuses
    assert not judge_events
    assert content == "Fast answer."


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
    assert content == "我补充了一条新的例子，并给出对应的 PMID 作为支持。"
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
