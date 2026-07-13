#!/usr/bin/env python3
"""Run the fixed ENSURE grounded-research benchmark against configured LLMs.

The evaluator intentionally bypasses the web chat workflow.  Each provider gets
the exact same frozen evidence and prompt, which isolates answer synthesis,
citation behavior, latency, token use, and estimated API cost from retrieval
variance.  Provider credentials are read with a SELECT from the backend's
``app_settings`` table and are never included in output artifacts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import statistics
import sys
import time
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


FLASK_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = FLASK_ROOT.parent
DEFAULT_DATASET = FLASK_ROOT / "evals" / "ensure_research_benchmark.json"
DEFAULT_OUTPUT_ROOT = FLASK_ROOT / "artifacts" / "research-model-eval"
SOURCE_ID_RE = re.compile(r"^S[1-9][0-9]*$")
CITATION_BRACKET_RE = re.compile(r"\[([^\]]+)\]")
CITATION_ID_RE = re.compile(r"\bS[1-9][0-9]*\b", flags=re.IGNORECASE)
SECRET_TOKEN_RE = re.compile(r"(?i)\b(?:sk|tp)-[A-Za-z0-9_-]{8,}\b")
BEARER_RE = re.compile(r"(?i)(Bearer\s+)[A-Za-z0-9._~+\-/=]{8,}")


class EvaluationConfigError(RuntimeError):
    """Raised when the benchmark or backend provider settings are invalid."""


@dataclass(frozen=True)
class ProviderRuntime:
    provider: str
    model: str
    base_url: str
    api_key: str = field(repr=False)
    pricing: Mapping[str, float] = field(default_factory=dict)
    pricing_source: str = ""

    def public_config(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "base_url": self.base_url,
            "credential_source": "app_settings",
            "pricing_cny_per_million_tokens": dict(self.pricing),
            "pricing_source": self.pricing_source,
        }


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_dataset(path: Path | str = DEFAULT_DATASET) -> dict[str, Any]:
    dataset_path = Path(path).expanduser().resolve()
    with dataset_path.open("r", encoding="utf-8") as handle:
        dataset = json.load(handle)
    validate_dataset(dataset)
    return dataset


def dataset_sha256(path: Path | str = DEFAULT_DATASET) -> str:
    return hashlib.sha256(Path(path).expanduser().resolve().read_bytes()).hexdigest()


def _require_nonempty_string(value: Any, label: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise EvaluationConfigError(f"{label} must be a non-empty string")
    return text


def validate_dataset(dataset: Mapping[str, Any]) -> None:
    if int(dataset.get("schema_version") or 0) != 1:
        raise EvaluationConfigError("dataset schema_version must be 1")
    _require_nonempty_string(dataset.get("benchmark_id"), "benchmark_id")

    prompt = dataset.get("prompt")
    if not isinstance(prompt, Mapping):
        raise EvaluationConfigError("prompt must be an object")
    _require_nonempty_string(prompt.get("system"), "prompt.system")

    models = dataset.get("models")
    if not isinstance(models, list) or not models:
        raise EvaluationConfigError("models must be a non-empty list")
    providers: set[str] = set()
    for index, model in enumerate(models):
        if not isinstance(model, Mapping):
            raise EvaluationConfigError(f"models[{index}] must be an object")
        provider = _require_nonempty_string(model.get("provider"), f"models[{index}].provider")
        if provider in providers:
            raise EvaluationConfigError(f"duplicate provider in models: {provider}")
        providers.add(provider)
        _require_nonempty_string(model.get("model"), f"models[{index}].model")
        _require_nonempty_string(model.get("base_url_setting"), f"models[{index}].base_url_setting")
        _require_nonempty_string(model.get("api_key_setting"), f"models[{index}].api_key_setting")
        pricing = model.get("pricing_cny_per_million_tokens")
        if not isinstance(pricing, Mapping):
            raise EvaluationConfigError(f"models[{index}].pricing_cny_per_million_tokens must be an object")
        for key in ("input_cache_hit", "input_cache_miss", "output"):
            try:
                value = float(pricing[key])
            except (KeyError, TypeError, ValueError) as exc:
                raise EvaluationConfigError(f"models[{index}] missing numeric price {key}") from exc
            if value < 0:
                raise EvaluationConfigError(f"models[{index}] price {key} cannot be negative")

    cases = dataset.get("cases")
    if not isinstance(cases, list) or not cases:
        raise EvaluationConfigError("cases must be a non-empty list")
    case_ids: set[str] = set()
    for case_index, case in enumerate(cases):
        if not isinstance(case, Mapping):
            raise EvaluationConfigError(f"cases[{case_index}] must be an object")
        case_id = _require_nonempty_string(case.get("id"), f"cases[{case_index}].id")
        if case_id in case_ids:
            raise EvaluationConfigError(f"duplicate case id: {case_id}")
        case_ids.add(case_id)
        _require_nonempty_string(case.get("question"), f"case {case_id}.question")

        sources = case.get("sources")
        if not isinstance(sources, list) or not sources:
            raise EvaluationConfigError(f"case {case_id} must have sources")
        source_ids: set[str] = set()
        for source_index, source in enumerate(sources):
            if not isinstance(source, Mapping):
                raise EvaluationConfigError(f"case {case_id} source {source_index} must be an object")
            source_id = _require_nonempty_string(source.get("id"), f"case {case_id} source id")
            if not SOURCE_ID_RE.fullmatch(source_id):
                raise EvaluationConfigError(f"case {case_id} has invalid source id {source_id!r}")
            if source_id in source_ids:
                raise EvaluationConfigError(f"case {case_id} has duplicate source id {source_id}")
            source_ids.add(source_id)
            _require_nonempty_string(source.get("text"), f"case {case_id} source {source_id}.text")

        required_source_ids = list(case.get("required_source_ids") or [])
        if not required_source_ids:
            raise EvaluationConfigError(f"case {case_id} must have required_source_ids")
        unknown_required = set(required_source_ids) - source_ids
        if unknown_required:
            raise EvaluationConfigError(
                f"case {case_id} requires unknown sources: {sorted(unknown_required)}"
            )

        facts = case.get("expected_facts")
        if not isinstance(facts, list) or not facts:
            raise EvaluationConfigError(f"case {case_id} must have expected_facts")
        fact_ids: set[str] = set()
        for fact_index, fact in enumerate(facts):
            if not isinstance(fact, Mapping):
                raise EvaluationConfigError(f"case {case_id} fact {fact_index} must be an object")
            fact_id = _require_nonempty_string(fact.get("id"), f"case {case_id} fact id")
            if fact_id in fact_ids:
                raise EvaluationConfigError(f"case {case_id} has duplicate fact id {fact_id}")
            fact_ids.add(fact_id)
            match = fact.get("match")
            if not isinstance(match, Mapping):
                raise EvaluationConfigError(f"case {case_id} fact {fact_id} needs match")
            all_of = match.get("all_of") or []
            any_of = match.get("any_of") or []
            groups = match.get("groups") or []
            if not isinstance(all_of, list) or not isinstance(any_of, list) or not isinstance(groups, list):
                raise EvaluationConfigError(f"case {case_id} fact {fact_id} match terms must be lists")
            if any(not isinstance(group, list) or not group for group in groups):
                raise EvaluationConfigError(f"case {case_id} fact {fact_id} match groups must be non-empty lists")
            if not all_of and not any_of and not groups:
                raise EvaluationConfigError(f"case {case_id} fact {fact_id} has no match terms")
            grouped_terms = [term for group in groups for term in group]
            if any(not str(term or "").strip() for term in list(all_of) + list(any_of) + grouped_terms):
                raise EvaluationConfigError(f"case {case_id} fact {fact_id} has an empty match term")
            fact_sources = set(fact.get("source_ids") or [])
            if not fact_sources or fact_sources - source_ids:
                raise EvaluationConfigError(
                    f"case {case_id} fact {fact_id} must reference known source_ids"
                )
            weight = float(fact.get("weight", 1.0))
            if weight <= 0:
                raise EvaluationConfigError(f"case {case_id} fact {fact_id} weight must be positive")


def normalize_text(value: Any) -> str:
    text = unicodedata.normalize("NFKC", str(value or "")).casefold()
    text = text.replace("–", "-").replace("—", "-").replace("‑", "-")
    return re.sub(r"\s+", " ", text).strip()


def fact_matches(answer: str, fact: Mapping[str, Any]) -> bool:
    normalized = normalize_text(answer)
    match = fact.get("match") or {}
    all_of = [normalize_text(term) for term in match.get("all_of") or []]
    any_of = [normalize_text(term) for term in match.get("any_of") or []]
    groups = [
        [normalize_text(term) for term in group]
        for group in match.get("groups") or []
    ]
    if any(term not in normalized for term in all_of):
        return False
    if any_of and not any(term in normalized for term in any_of):
        return False
    if any(not any(term in normalized for term in group) for group in groups):
        return False
    return bool(all_of or any_of or groups)


def extract_citations(answer: str) -> list[str]:
    citations: list[str] = []
    for bracket in CITATION_BRACKET_RE.findall(str(answer or "")):
        for source_id in CITATION_ID_RE.findall(bracket):
            citations.append(source_id.upper())
    return citations


def _fact_has_nearby_valid_citation(
    answer: str,
    fact: Mapping[str, Any],
    allowed_sources: set[str],
    window_chars: int = 420,
) -> bool:
    if not fact_matches(answer, fact):
        return False
    text = str(answer or "")
    for match in CITATION_BRACKET_RE.finditer(text):
        citation_ids = {item.upper() for item in CITATION_ID_RE.findall(match.group(1))}
        if not citation_ids.intersection(allowed_sources):
            continue
        start = max(0, match.start() - window_chars)
        end = min(len(text), match.end() + 80)
        if fact_matches(text[start:end], fact):
            return True
    return False


def score_answer(answer: str, case: Mapping[str, Any]) -> dict[str, Any]:
    source_ids = {str(source["id"]) for source in case.get("sources") or []}
    required_source_ids = {str(item) for item in case.get("required_source_ids") or []}
    citations = extract_citations(answer)
    valid_citations = [citation for citation in citations if citation in source_ids]
    invalid_citations = [citation for citation in citations if citation not in source_ids]

    fact_results: list[dict[str, Any]] = []
    earned_weight = 0.0
    total_weight = 0.0
    cited_fact_weight = 0.0
    matched_fact_weight = 0.0
    for fact in case.get("expected_facts") or []:
        weight = float(fact.get("weight", 1.0))
        matched = fact_matches(answer, fact)
        allowed = {str(source_id) for source_id in fact.get("source_ids") or []}
        citation_supported = matched and _fact_has_nearby_valid_citation(answer, fact, allowed)
        total_weight += weight
        if matched:
            earned_weight += weight
            matched_fact_weight += weight
        if citation_supported:
            cited_fact_weight += weight
        fact_results.append(
            {
                "id": str(fact.get("id") or ""),
                "description": str(fact.get("description") or ""),
                "matched": matched,
                "citation_supported": citation_supported,
                "source_ids": sorted(allowed),
                "weight": weight,
            }
        )

    accuracy = earned_weight / total_weight if total_weight else 0.0
    citation_validity = len(valid_citations) / len(citations) if citations else 0.0
    valid_unique = set(valid_citations)
    citation_coverage = (
        len(valid_unique.intersection(required_source_ids)) / len(required_source_ids)
        if required_source_ids
        else 1.0
    )
    fact_citation_support = (
        cited_fact_weight / matched_fact_weight if matched_fact_weight else 0.0
    )
    grounded_score = 0.70 * accuracy + 0.20 * citation_validity + 0.10 * citation_coverage

    return {
        "accuracy": round(accuracy, 6),
        "matched_facts": sum(1 for item in fact_results if item["matched"]),
        "total_facts": len(fact_results),
        "fact_results": fact_results,
        "citation_count": len(citations),
        "valid_citation_count": len(valid_citations),
        "citation_validity": round(citation_validity, 6),
        "citation_coverage": round(citation_coverage, 6),
        "fact_citation_support": round(fact_citation_support, 6),
        "cited_source_ids": sorted(valid_unique),
        "invalid_source_ids": sorted(set(invalid_citations)),
        "grounded_score": round(grounded_score, 6),
    }


def build_messages(dataset: Mapping[str, Any], case: Mapping[str, Any]) -> list[dict[str, str]]:
    prompt = dataset.get("prompt") or {}
    evidence_header = str(prompt.get("evidence_header") or "Frozen evidence")
    evidence_blocks = []
    for source in case.get("sources") or []:
        source_id = str(source.get("id") or "")
        title = str(source.get("title") or "").strip()
        provenance = str(source.get("provenance") or "").strip()
        label = f"[{source_id}]"
        if title:
            label += f" {title}"
        if provenance:
            label += f" ({provenance})"
        evidence_blocks.append(label + "\n" + str(source.get("text") or "").strip())
    user_content = (
        "Question:\n"
        + str(case.get("question") or "").strip()
        + f"\n\n{evidence_header}:\n"
        + "\n\n".join(evidence_blocks)
    )
    return [
        {"role": "system", "content": str(prompt.get("system") or "").strip()},
        {"role": "user", "content": user_content},
    ]


def estimate_tokens(text: str) -> int:
    """Conservative tokenizer-free estimate for mixed Chinese/English text."""
    value = str(text or "")
    cjk = len(re.findall(r"[\u3400-\u9fff\uf900-\ufaff\u3040-\u30ff\uac00-\ud7af]", value))
    remainder = re.sub(r"[\u3400-\u9fff\uf900-\ufaff\u3040-\u30ff\uac00-\ud7af]", "", value)
    non_space = len(re.sub(r"\s+", "", remainder))
    return max(1, cjk + math.ceil(non_space / 4))


def normalize_usage(
    raw_usage: Mapping[str, Any] | None,
    messages: Sequence[Mapping[str, Any]],
    answer: str,
) -> dict[str, Any]:
    raw = dict(raw_usage or {})
    input_tokens = int(raw.get("prompt_tokens") or raw.get("input_tokens") or 0)
    output_tokens = int(raw.get("completion_tokens") or raw.get("output_tokens") or 0)
    total_tokens = int(raw.get("total_tokens") or 0)

    prompt_details = raw.get("prompt_tokens_details") or raw.get("input_tokens_details") or {}
    completion_details = raw.get("completion_tokens_details") or raw.get("output_tokens_details") or {}
    if not isinstance(prompt_details, Mapping):
        prompt_details = {}
    if not isinstance(completion_details, Mapping):
        completion_details = {}
    cached_tokens = int(
        raw.get("prompt_cache_hit_tokens")
        or raw.get("cache_read_input_tokens")
        or prompt_details.get("cached_tokens")
        or prompt_details.get("cache_read_tokens")
        or 0
    )
    reasoning_tokens = int(completion_details.get("reasoning_tokens") or raw.get("reasoning_tokens") or 0)

    estimated_input = estimate_tokens(json.dumps(list(messages), ensure_ascii=False, separators=(",", ":")))
    estimated_output = estimate_tokens(answer) if answer else 0
    used_estimate = False
    used_api = bool(input_tokens or output_tokens or total_tokens)
    if input_tokens <= 0:
        input_tokens = estimated_input
        used_estimate = True
    if output_tokens <= 0 and answer:
        output_tokens = estimated_output
        used_estimate = True
    if total_tokens <= 0:
        total_tokens = input_tokens + output_tokens
    cached_tokens = min(max(0, cached_tokens), input_tokens)
    if used_api and used_estimate:
        source = "api+estimated"
    elif used_api:
        source = "api"
    else:
        source = "estimated"
    return {
        "input_tokens": input_tokens,
        "cached_input_tokens": cached_tokens,
        "uncached_input_tokens": max(0, input_tokens - cached_tokens),
        "output_tokens": output_tokens,
        "reasoning_tokens": reasoning_tokens,
        "total_tokens": total_tokens,
        "source": source,
    }


def estimate_cost_cny(usage: Mapping[str, Any], pricing: Mapping[str, Any]) -> float:
    cached = int(usage.get("cached_input_tokens") or 0)
    uncached = int(usage.get("uncached_input_tokens") or 0)
    output = int(usage.get("output_tokens") or 0)
    cost = (
        cached * float(pricing.get("input_cache_hit") or 0)
        + uncached * float(pricing.get("input_cache_miss") or 0)
        + output * float(pricing.get("output") or 0)
    ) / 1_000_000
    return round(cost, 8)


def sanitize_text(value: Any, secrets: Iterable[str] = ()) -> str:
    text = str(value or "")
    for secret in secrets:
        if secret:
            text = text.replace(secret, "[REDACTED]")
    text = SECRET_TOKEN_RE.sub("[REDACTED]", text)
    text = BEARER_RE.sub(r"\1[REDACTED]", text)
    return text


def assert_no_secrets(payload: Any, secrets: Iterable[str]) -> None:
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    for secret in secrets:
        if secret and secret in serialized:
            raise RuntimeError("refusing to write an artifact containing a provider credential")
    if SECRET_TOKEN_RE.search(serialized) or BEARER_RE.search(serialized):
        raise RuntimeError("refusing to write an artifact containing a key-like token")


def _content_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, Mapping):
                parts.append(str(item.get("text") or item.get("content") or ""))
        return "".join(parts)
    return ""


def _merge_usage(current: dict[str, Any], candidate: Any) -> dict[str, Any]:
    if not isinstance(candidate, Mapping):
        return current
    merged = dict(current)
    for key, value in candidate.items():
        if value is not None:
            merged[key] = value
    return merged


def stream_chat_completion(
    runtime: ProviderRuntime,
    messages: Sequence[Mapping[str, str]],
    *,
    timeout: float,
    temperature: float | None,
    thinking: str,
    session: Any = None,
) -> dict[str, Any]:
    """Call an OpenAI-compatible streaming endpoint and capture TTFT/usage."""
    try:
        import requests
    except ImportError as exc:  # pragma: no cover - dependency is in requirements.txt
        raise EvaluationConfigError("requests is required for live evaluation") from exc

    client = session or requests.Session()
    url = runtime.base_url.rstrip("/")
    if not url.endswith("/chat/completions"):
        url += "/chat/completions"
    headers = {
        "Authorization": f"Bearer {runtime.api_key}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    }
    base_payload: dict[str, Any] = {
        "model": runtime.model,
        "messages": list(messages),
        "stream": True,
        "thinking": {"type": "enabled" if thinking == "enabled" else "disabled"},
    }
    if temperature is not None:
        base_payload["temperature"] = float(temperature)

    secrets = [runtime.api_key]
    last_error = ""
    for include_usage in (True, False):
        payload = dict(base_payload)
        if include_usage:
            payload["stream_options"] = {"include_usage": True}
        started = time.perf_counter()
        try:
            response = client.post(
                url,
                json=payload,
                headers=headers,
                stream=True,
                timeout=(10, float(timeout)),
            )
        except Exception as exc:
            return {
                "ok": False,
                "http_status": None,
                "error": sanitize_text(type(exc).__name__, secrets),
                "answer": "",
                "ttft_seconds": None,
                "total_seconds": round(time.perf_counter() - started, 6),
                "raw_usage": {},
                "stream_options_include_usage": include_usage,
            }

        if response.status_code >= 400:
            body = sanitize_text(response.text[:800], secrets)
            last_error = f"HTTP {response.status_code}: {body}".strip()
            response.close()
            if include_usage and response.status_code == 400:
                continue
            return {
                "ok": False,
                "http_status": response.status_code,
                "error": last_error,
                "answer": "",
                "ttft_seconds": None,
                "total_seconds": round(time.perf_counter() - started, 6),
                "raw_usage": {},
                "stream_options_include_usage": include_usage,
            }

        response.encoding = "utf-8"
        answer_parts: list[str] = []
        raw_usage: dict[str, Any] = {}
        ttft: float | None = None
        finish_reason: str | None = None
        parse_error = ""
        try:
            content_type = str(response.headers.get("Content-Type") or "").lower()
            if "text/event-stream" not in content_type and "application/json" in content_type:
                data = response.json() or {}
                raw_usage = _merge_usage(raw_usage, data.get("usage"))
                choices = data.get("choices") or []
                if choices:
                    message = choices[0].get("message") or {}
                    content = _content_text(message.get("content"))
                    if content:
                        ttft = time.perf_counter() - started
                        answer_parts.append(content)
                    finish_reason = choices[0].get("finish_reason")
            else:
                for line in response.iter_lines(chunk_size=1, decode_unicode=True):
                    if not line:
                        continue
                    text_line = str(line)
                    if not text_line.startswith("data:"):
                        continue
                    raw = text_line[5:].strip()
                    if not raw:
                        continue
                    if raw == "[DONE]":
                        break
                    try:
                        data = json.loads(raw)
                    except json.JSONDecodeError:
                        continue
                    raw_usage = _merge_usage(raw_usage, data.get("usage"))
                    choices = data.get("choices") or []
                    if not choices:
                        continue
                    choice = choices[0] or {}
                    delta = choice.get("delta") or {}
                    content = _content_text(delta.get("content"))
                    if content:
                        if ttft is None:
                            ttft = time.perf_counter() - started
                        answer_parts.append(content)
                    if choice.get("finish_reason") is not None:
                        finish_reason = str(choice.get("finish_reason"))
        except Exception as exc:
            parse_error = sanitize_text(type(exc).__name__, secrets)
        finally:
            response.close()

        total = time.perf_counter() - started
        answer = "".join(answer_parts).strip()
        ok = bool(answer) and not parse_error
        return {
            "ok": ok,
            "http_status": response.status_code,
            "error": parse_error if parse_error else ("empty model response" if not answer else ""),
            "answer": answer,
            "ttft_seconds": round(ttft, 6) if ttft is not None else None,
            "total_seconds": round(total, 6),
            "finish_reason": finish_reason,
            "raw_usage": raw_usage,
            "stream_options_include_usage": include_usage,
        }

    return {
        "ok": False,
        "http_status": 400,
        "error": last_error or "request rejected",
        "answer": "",
        "ttft_seconds": None,
        "total_seconds": 0.0,
        "raw_usage": {},
        "stream_options_include_usage": False,
    }


def _read_app_settings(setting_keys: Sequence[str]) -> dict[str, str]:
    """Read only the requested settings with a single SELECT.

    Importantly, this does not call ``create_app`` or ``get_llm_settings``;
    those helpers ensure/create defaults.  The evaluator must not mutate live
    settings merely by loading credentials.
    """
    try:
        from dotenv import load_dotenv
        from sqlalchemy import create_engine, text
    except ImportError as exc:  # pragma: no cover - dependencies are declared
        raise EvaluationConfigError("python-dotenv and SQLAlchemy are required") from exc

    load_dotenv(FLASK_ROOT / ".env", override=False)
    if str(FLASK_ROOT) not in sys.path:
        sys.path.insert(0, str(FLASK_ROOT))
    from config import Config  # pylint: disable=import-outside-toplevel

    keys = list(dict.fromkeys(str(item) for item in setting_keys))
    placeholders = ", ".join(f":key_{index}" for index in range(len(keys)))
    params = {f"key_{index}": key for index, key in enumerate(keys)}
    query = text(
        "SELECT setting_key, setting_value FROM app_settings "
        f"WHERE setting_key IN ({placeholders})"
    )
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
    try:
        try:
            with engine.connect() as connection:
                rows = connection.execute(query, params)
                return {str(row[0]): str(row[1] or "").strip() for row in rows}
        except Exception as exc:
            raise EvaluationConfigError(
                "unable to read the required app_settings rows"
            ) from exc
    finally:
        engine.dispose()


def load_provider_runtimes(
    dataset: Mapping[str, Any],
    selected_providers: Sequence[str] | None = None,
) -> list[ProviderRuntime]:
    selected = {str(item).strip() for item in selected_providers or [] if str(item).strip()}
    model_specs = [
        spec for spec in dataset.get("models") or []
        if not selected or str(spec.get("provider")) in selected
    ]
    available = {str(spec.get("provider")) for spec in dataset.get("models") or []}
    unknown = selected - available
    if unknown:
        raise EvaluationConfigError(f"unknown providers requested: {sorted(unknown)}")
    setting_keys = ["llm_timeout"]
    for spec in model_specs:
        setting_keys.extend([str(spec["base_url_setting"]), str(spec["api_key_setting"])])
    settings = _read_app_settings(setting_keys)

    runtimes: list[ProviderRuntime] = []
    missing: list[str] = []
    for spec in model_specs:
        provider = str(spec["provider"])
        base_key = str(spec["base_url_setting"])
        api_key_key = str(spec["api_key_setting"])
        base_url = str(settings.get(base_key) or "").strip()
        api_key = str(settings.get(api_key_key) or "").strip()
        if not base_url:
            missing.append(f"{provider}:{base_key}")
        if not api_key:
            missing.append(f"{provider}:{api_key_key}")
        if base_url and api_key:
            runtimes.append(
                ProviderRuntime(
                    provider=provider,
                    model=str(spec["model"]),
                    base_url=base_url,
                    api_key=api_key,
                    pricing={
                        key: float(value)
                        for key, value in dict(spec["pricing_cny_per_million_tokens"]).items()
                    },
                    pricing_source=str(spec.get("pricing_source") or ""),
                )
            )
    if missing:
        raise EvaluationConfigError(
            "required app_settings values are missing: " + ", ".join(missing)
        )
    return runtimes


def select_cases(
    dataset: Mapping[str, Any],
    case_ids: Sequence[str] | None = None,
    limit: int | None = None,
) -> list[Mapping[str, Any]]:
    cases = list(dataset.get("cases") or [])
    requested = [str(item) for item in case_ids or []]
    if requested:
        by_id = {str(case["id"]): case for case in cases}
        missing = [case_id for case_id in requested if case_id not in by_id]
        if missing:
            raise EvaluationConfigError(f"unknown benchmark cases: {missing}")
        cases = [by_id[case_id] for case_id in requested]
    if limit is not None:
        if limit <= 0:
            raise EvaluationConfigError("--limit must be positive")
        cases = cases[:limit]
    return cases


def run_benchmark(
    dataset: Mapping[str, Any],
    dataset_path: Path,
    runtimes: Sequence[ProviderRuntime],
    cases: Sequence[Mapping[str, Any]],
    *,
    timeout: float,
    run_id: str,
) -> dict[str, Any]:
    try:
        import requests
    except ImportError as exc:  # pragma: no cover
        raise EvaluationConfigError("requests is required for live evaluation") from exc

    prompt = dataset.get("prompt") or {}
    temperature = prompt.get("temperature")
    thinking = str(prompt.get("thinking") or "disabled").strip().lower()
    if thinking not in {"enabled", "disabled"}:
        raise EvaluationConfigError("prompt.thinking must be enabled or disabled")
    sessions = {runtime.provider: requests.Session() for runtime in runtimes}
    results: list[dict[str, Any]] = []
    started = time.perf_counter()
    try:
        for case in cases:
            messages = build_messages(dataset, case)
            for runtime in runtimes:
                print(
                    f"[{len(results) + 1}/{len(cases) * len(runtimes)}] "
                    f"{runtime.provider}/{runtime.model} :: {case['id']}",
                    flush=True,
                )
                response = stream_chat_completion(
                    runtime,
                    messages,
                    timeout=timeout,
                    temperature=float(temperature) if temperature is not None else None,
                    thinking=thinking,
                    session=sessions[runtime.provider],
                )
                answer = str(response.get("answer") or "")
                score = score_answer(answer, case)
                if response.get("ok"):
                    usage = normalize_usage(response.get("raw_usage"), messages, answer)
                    estimated_cost = estimate_cost_cny(usage, runtime.pricing)
                else:
                    usage = {
                        "input_tokens": 0,
                        "cached_input_tokens": 0,
                        "uncached_input_tokens": 0,
                        "output_tokens": 0,
                        "reasoning_tokens": 0,
                        "total_tokens": 0,
                        "source": "none",
                    }
                    estimated_cost = 0.0
                results.append(
                    {
                        "case_id": str(case["id"]),
                        "category": str(case.get("category") or ""),
                        "question": str(case.get("question") or ""),
                        "provider": runtime.provider,
                        "model": runtime.model,
                        "ok": bool(response.get("ok")),
                        "http_status": response.get("http_status"),
                        "error": sanitize_text(response.get("error") or "", [runtime.api_key]),
                        "answer": answer,
                        "timing": {
                            "ttft_seconds": response.get("ttft_seconds"),
                            "total_seconds": response.get("total_seconds"),
                        },
                        "finish_reason": response.get("finish_reason"),
                        "stream_options_include_usage": bool(
                            response.get("stream_options_include_usage")
                        ),
                        "usage": usage,
                        "estimated_cost_cny": estimated_cost,
                        "score": score,
                    }
                )
    finally:
        for session in sessions.values():
            session.close()

    elapsed = time.perf_counter() - started
    resolved_dataset_path = dataset_path.resolve()
    try:
        displayed_dataset_path = str(resolved_dataset_path.relative_to(REPO_ROOT))
    except ValueError:
        displayed_dataset_path = str(resolved_dataset_path)
    payload: dict[str, Any] = {
        "schema_version": 1,
        "run_id": run_id,
        "created_at": utc_now_iso(),
        "benchmark": {
            "id": str(dataset.get("benchmark_id") or ""),
            "title": str(dataset.get("title") or ""),
            "snapshot_date": str(dataset.get("snapshot_date") or ""),
            "dataset_path": displayed_dataset_path,
            "dataset_sha256": dataset_sha256(dataset_path),
            "case_count": len(cases),
            "mode": "fixed-evidence direct provider comparison",
        },
        "configuration": {
            "providers": [runtime.public_config() for runtime in runtimes],
            "timeout_seconds": timeout,
            "temperature": temperature,
            "thinking": thinking,
            "credentials": "read by SELECT from Flask app_settings; never serialized",
        },
        "elapsed_seconds": round(elapsed, 6),
        "results": results,
    }
    payload["summary"] = summarize_results(results)
    return payload


def _percentile(values: Sequence[float], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(float(value) for value in values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * percentile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def summarize_results(results: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
    for result in results:
        key = (str(result.get("provider") or ""), str(result.get("model") or ""))
        groups.setdefault(key, []).append(result)
    summary: list[dict[str, Any]] = []
    for (provider, model), items in groups.items():
        accuracies = [float((item.get("score") or {}).get("accuracy") or 0) for item in items]
        validities = [float((item.get("score") or {}).get("citation_validity") or 0) for item in items]
        coverages = [float((item.get("score") or {}).get("citation_coverage") or 0) for item in items]
        grounded = [float((item.get("score") or {}).get("grounded_score") or 0) for item in items]
        ttft = [
            float((item.get("timing") or {}).get("ttft_seconds"))
            for item in items
            if (item.get("timing") or {}).get("ttft_seconds") is not None
        ]
        totals = [
            float((item.get("timing") or {}).get("total_seconds"))
            for item in items
            if (item.get("timing") or {}).get("total_seconds") is not None
        ]
        summary.append(
            {
                "provider": provider,
                "model": model,
                "cases": len(items),
                "successful_cases": sum(1 for item in items if item.get("ok")),
                "accuracy": round(statistics.fmean(accuracies), 6) if accuracies else 0.0,
                "citation_validity": round(statistics.fmean(validities), 6) if validities else 0.0,
                "citation_coverage": round(statistics.fmean(coverages), 6) if coverages else 0.0,
                "grounded_score": round(statistics.fmean(grounded), 6) if grounded else 0.0,
                "median_ttft_seconds": round(statistics.median(ttft), 6) if ttft else None,
                "p95_ttft_seconds": round(_percentile(ttft, 0.95), 6) if ttft else None,
                "median_total_seconds": round(statistics.median(totals), 6) if totals else None,
                "p95_total_seconds": round(_percentile(totals, 0.95), 6) if totals else None,
                "input_tokens": sum(int((item.get("usage") or {}).get("input_tokens") or 0) for item in items),
                "cached_input_tokens": sum(
                    int((item.get("usage") or {}).get("cached_input_tokens") or 0) for item in items
                ),
                "output_tokens": sum(int((item.get("usage") or {}).get("output_tokens") or 0) for item in items),
                "total_tokens": sum(int((item.get("usage") or {}).get("total_tokens") or 0) for item in items),
                "estimated_cost_cny": round(
                    sum(float(item.get("estimated_cost_cny") or 0) for item in items), 8
                ),
            }
        )
    return summary


def _md_cell(value: Any) -> str:
    if value is None:
        return "—"
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_markdown(payload: Mapping[str, Any]) -> str:
    benchmark = payload.get("benchmark") or {}
    lines = [
        f"# {_md_cell(benchmark.get('title') or 'ENSURE research model benchmark')}",
        "",
        f"- Run: `{_md_cell(payload.get('run_id'))}`",
        f"- Created: `{_md_cell(payload.get('created_at'))}`",
        f"- Dataset: `{_md_cell(benchmark.get('dataset_path'))}`",
        f"- Dataset SHA-256: `{_md_cell(benchmark.get('dataset_sha256'))}`",
        f"- Cases: `{_md_cell(benchmark.get('case_count'))}`",
        "- Method: both models receive the same frozen evidence and citation labels; retrieval is not part of this benchmark.",
        "",
        "## Summary",
        "",
        "| Provider | Model | Success | Accuracy | [S#] validity | Source coverage | Grounded score | Median TTFT | Median total | Tokens | Est. CNY |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in payload.get("summary") or []:
        lines.append(
            "| {provider} | {model} | {success}/{cases} | {accuracy:.1%} | {validity:.1%} | "
            "{coverage:.1%} | {grounded:.1%} | {ttft} | {total} | {tokens} | {cost:.6f} |".format(
                provider=_md_cell(item.get("provider")),
                model=_md_cell(item.get("model")),
                success=int(item.get("successful_cases") or 0),
                cases=int(item.get("cases") or 0),
                accuracy=float(item.get("accuracy") or 0),
                validity=float(item.get("citation_validity") or 0),
                coverage=float(item.get("citation_coverage") or 0),
                grounded=float(item.get("grounded_score") or 0),
                ttft=(
                    f"{float(item['median_ttft_seconds']):.3f}s"
                    if item.get("median_ttft_seconds") is not None
                    else "—"
                ),
                total=(
                    f"{float(item['median_total_seconds']):.3f}s"
                    if item.get("median_total_seconds") is not None
                    else "—"
                ),
                tokens=int(item.get("total_tokens") or 0),
                cost=float(item.get("estimated_cost_cny") or 0),
            )
        )

    lines.extend(["", "## Per-case results", ""])
    for result in payload.get("results") or []:
        score = result.get("score") or {}
        timing = result.get("timing") or {}
        usage = result.get("usage") or {}
        lines.extend(
            [
                f"### `{_md_cell(result.get('case_id'))}` — {_md_cell(result.get('provider'))}/{_md_cell(result.get('model'))}",
                "",
                f"- Status: `{'ok' if result.get('ok') else 'error'}`; HTTP `{_md_cell(result.get('http_status'))}`",
                f"- Accuracy: `{float(score.get('accuracy') or 0):.1%}` ({int(score.get('matched_facts') or 0)}/{int(score.get('total_facts') or 0)} facts)",
                f"- Citation validity / coverage: `{float(score.get('citation_validity') or 0):.1%}` / `{float(score.get('citation_coverage') or 0):.1%}`",
                f"- TTFT / total: `{_md_cell(timing.get('ttft_seconds'))}` / `{_md_cell(timing.get('total_seconds'))}` seconds",
                f"- Tokens: input `{int(usage.get('input_tokens') or 0)}`, output `{int(usage.get('output_tokens') or 0)}`, source `{_md_cell(usage.get('source'))}`",
                f"- Estimated cost: `¥{float(result.get('estimated_cost_cny') or 0):.8f}`",
            ]
        )
        if result.get("error"):
            lines.append(f"- Error: `{_md_cell(result.get('error'))}`")
        lines.extend(["", "Answer:", ""])
        answer = str(result.get("answer") or "(no answer)")
        lines.extend(["> " + line if line else ">" for line in answer.splitlines()])
        lines.append("")

    lines.extend(
        [
            "## Interpretation notes",
            "",
            "- Accuracy is deterministic keyword/fact coverage against the frozen expectations; it is not a substitute for expert review.",
            "- `[S#]` validity measures whether cited labels exist in the supplied case. Source coverage measures whether required sources were cited.",
            "- Token counts use provider-reported usage when present; otherwise the report marks them as tokenizer-free estimates.",
            "- Cost is an estimate from the pricing snapshot recorded in the dataset and may differ from the provider bill, cache behavior, or later pricing.",
            "",
        ]
    )
    return "\n".join(lines)


def write_artifacts(
    payload: Mapping[str, Any],
    output_root: Path | str,
    secrets: Iterable[str],
) -> tuple[Path, Path]:
    secret_values = tuple(secrets)
    assert_no_secrets(payload, secret_values)
    markdown = render_markdown(payload)
    assert_no_secrets(markdown, secret_values)
    output_dir = Path(output_root).expanduser().resolve() / str(payload.get("run_id") or "run")
    output_dir.mkdir(parents=True, exist_ok=False)
    json_path = output_dir / "results.json"
    markdown_path = output_dir / "report.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(markdown, encoding="utf-8")
    return json_path, markdown_path


def _synthetic_perfect_answer(case: Mapping[str, Any]) -> str:
    lines = []
    for fact in case.get("expected_facts") or []:
        match = fact.get("match") or {}
        terms = [str(term) for term in match.get("all_of") or []]
        any_terms = list(match.get("any_of") or [])
        if any_terms:
            terms.append(str(any_terms[0]))
        for group in match.get("groups") or []:
            if group:
                terms.append(str(group[0]))
        citations = "".join(f"[{source_id}]" for source_id in fact.get("source_ids") or [])
        lines.append(" ".join(terms) + " " + citations)
    return "\n".join(lines)


def run_dry_run(dataset_path: Path | str) -> dict[str, Any]:
    dataset = load_dataset(dataset_path)
    perfect_scores = []
    for case in dataset.get("cases") or []:
        answer = _synthetic_perfect_answer(case)
        score = score_answer(answer, case)
        if score["accuracy"] != 1.0:
            raise AssertionError(f"synthetic perfect answer did not score 100% for {case['id']}")
        if score["citation_validity"] != 1.0 or score["citation_coverage"] != 1.0:
            raise AssertionError(f"synthetic citations did not score 100% for {case['id']}")
        perfect_scores.append(score)

    first_case = (dataset.get("cases") or [])[0]
    invalid = score_answer(_synthetic_perfect_answer(first_case) + " [S999]", first_case)
    if invalid["citation_validity"] >= 1.0 or "S999" not in invalid["invalid_source_ids"]:
        raise AssertionError("invalid citation smoke test failed")
    usage = {
        "cached_input_tokens": 100,
        "uncached_input_tokens": 200,
        "output_tokens": 50,
    }
    cost = estimate_cost_cny(
        usage,
        {"input_cache_hit": 0.025, "input_cache_miss": 3.0, "output": 6.0},
    )
    if not math.isclose(cost, 0.0009025, rel_tol=0, abs_tol=1e-12):
        raise AssertionError("cost calculation smoke test failed")
    return {
        "ok": True,
        "benchmark_id": dataset.get("benchmark_id"),
        "dataset_sha256": dataset_sha256(dataset_path),
        "cases_validated": len(perfect_scores),
        "models_validated": len(dataset.get("models") or []),
        "checks": [
            "dataset schema",
            "perfect fact scoring",
            "valid and invalid [S#] citations",
            "cost calculation",
            "no database or network access",
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--provider", action="append", dest="providers", help="Provider to run; repeatable")
    parser.add_argument("--case", action="append", dest="case_ids", help="Case id to run; repeatable")
    parser.add_argument("--limit", type=int, help="Run only the first N selected cases")
    parser.add_argument("--timeout", type=float, help="Per-request read timeout in seconds")
    parser.add_argument("--run-id", help="Artifact directory name; defaults to a UTC timestamp")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate dataset/scoring with deterministic fixtures; do not read DB, call APIs, or write artifacts",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.dry_run:
            print(json.dumps(run_dry_run(args.dataset), ensure_ascii=False, indent=2))
            return 0

        dataset_path = args.dataset.expanduser().resolve()
        dataset = load_dataset(dataset_path)
        cases = select_cases(dataset, args.case_ids, args.limit)
        runtimes = load_provider_runtimes(dataset, args.providers)
        timeout = float(args.timeout or 0)
        if timeout <= 0:
            settings = _read_app_settings(["llm_timeout"])
            timeout = float(settings.get("llm_timeout") or 120)
        run_id = args.run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", run_id):
            raise EvaluationConfigError(
                "--run-id must contain only letters, digits, dot, underscore, or dash"
            )
        payload = run_benchmark(
            dataset,
            dataset_path,
            runtimes,
            cases,
            timeout=timeout,
            run_id=run_id,
        )
        secrets = [runtime.api_key for runtime in runtimes]
        json_path, markdown_path = write_artifacts(payload, args.output_dir, secrets)
        print("\nSummary:")
        for item in payload.get("summary") or []:
            print(
                f"- {item['provider']}/{item['model']}: "
                f"accuracy={item['accuracy']:.1%}, citations={item['citation_validity']:.1%}, "
                f"median TTFT={item['median_ttft_seconds']}, total={item['median_total_seconds']}, "
                f"estimated CNY={item['estimated_cost_cny']:.8f}"
            )
        print(f"JSON: {json_path}")
        print(f"Markdown: {markdown_path}")
        return 0 if all(result.get("ok") for result in payload.get("results") or []) else 2
    except (EvaluationConfigError, OSError, ValueError) as exc:
        print(f"ERROR: {sanitize_text(type(exc).__name__ + ': ' + str(exc))}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
