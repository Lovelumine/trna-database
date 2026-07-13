from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


FLASK_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = FLASK_ROOT / "scripts" / "evaluate_research_models.py"
DATASET_PATH = FLASK_ROOT / "evals" / "ensure_research_benchmark.json"
if str(SCRIPT_PATH.parent) not in sys.path:
    sys.path.insert(0, str(SCRIPT_PATH.parent))
import evaluate_research_models as evaluator  # noqa: E402


def test_fixed_dataset_validates_and_contains_stable_records():
    dataset = evaluator.load_dataset(DATASET_PATH)

    assert dataset["benchmark_id"] == "ensure-research-grounded-v1"
    assert {model["model"] for model in dataset["models"]} == {
        "mimo-v2.5-pro",
        "deepseek-v4-pro",
    }
    cases = {case["id"]: case for case in dataset["cases"]}
    assert "ensure-publication-metadata" in cases
    assert "engineered-stable-record-pair-1206-1211" in cases
    stable_text = json.dumps(cases["engineered-stable-record-pair-1206-1211"], ensure_ascii=False)
    for expected in (
        "mCherry-STOP-GFP",
        "Leu(CUA)",
        "Homo sapiens",
        "eGFP",
        "Leu(UCA)",
        "Mus musculus",
        "41261131",
    ):
        assert expected in stable_text


def test_scoring_rewards_expected_facts_and_valid_citations():
    dataset = evaluator.load_dataset(DATASET_PATH)
    case = next(case for case in dataset["cases"] if case["id"] == "ensure-publication-metadata")
    answer = (
        "The paper is ENSURE: the Encyclopedia of Suppressor tRNA with an AI assistant [S1]. "
        "It appeared in Nucleic Acids Research in 2025 [S1]. "
        "DOI 10.1093/nar/gkaf1062; PMID 41160884 [S1]."
    )

    score = evaluator.score_answer(answer, case)

    assert score["accuracy"] == 1.0
    assert score["citation_validity"] == 1.0
    assert score["citation_coverage"] == 1.0
    assert score["invalid_source_ids"] == []


def test_scoring_detects_invalid_and_missing_citations():
    dataset = evaluator.load_dataset(DATASET_PATH)
    case = next(case for case in dataset["cases"] if case["id"] == "ensure-publication-metadata")
    answer = "ENSURE: the Encyclopedia of Suppressor tRNA with an AI assistant. PMID 41160884 [S99]."

    score = evaluator.score_answer(answer, case)

    assert 0 < score["accuracy"] < 1
    assert score["citation_validity"] == 0
    assert score["citation_coverage"] == 0
    assert score["invalid_source_ids"] == ["S99"]


def test_multilingual_match_groups_accept_equivalent_scientific_terms():
    fact = {
        "match": {
            "groups": [
                ["natural", "天然"],
                ["readthrough", "通读"],
                ["reaction system", "反应体系", "反应系统"],
            ]
        }
    }

    assert evaluator.fact_matches("天然 sup-tRNA 的反应系统与通读效率", fact)
    assert evaluator.fact_matches("Natural sup-tRNA readthrough reaction system", fact)
    assert not evaluator.fact_matches("天然 sup-tRNA 的结构信息", fact)


def test_usage_falls_back_to_explicitly_marked_estimate():
    messages = [{"role": "user", "content": "请概括 ENSURE。"}]

    usage = evaluator.normalize_usage({}, messages, "ENSURE 是一个数据库。")

    assert usage["source"] == "estimated"
    assert usage["input_tokens"] > 0
    assert usage["output_tokens"] > 0
    assert usage["total_tokens"] == usage["input_tokens"] + usage["output_tokens"]


def test_cost_uses_declared_cny_prices_without_currency_conversion():
    usage = {
        "cached_input_tokens": 100,
        "uncached_input_tokens": 200,
        "output_tokens": 50,
    }
    pricing = {
        "input_cache_hit": 0.025,
        "input_cache_miss": 3.0,
        "output": 6.0,
    }

    assert evaluator.estimate_cost_cny(usage, pricing) == pytest.approx(0.0009025)


def test_artifact_secret_guard_rejects_key_like_values(tmp_path: Path):
    secret = "sk-unit-test-secret-123456789"
    payload = {"run_id": "test", "answer": f"accidentally echoed {secret}"}

    with pytest.raises(RuntimeError, match="credential|key-like"):
        evaluator.write_artifacts(payload, tmp_path, [secret])
    assert not (tmp_path / "test").exists()


def test_provider_runtime_repr_and_public_config_omit_secret():
    secret = "sk-unit-test-secret-123456789"
    runtime = evaluator.ProviderRuntime(
        provider="xiaomi",
        model="mimo-v2.5-pro",
        base_url="https://api.example.invalid/v1",
        api_key=secret,
        pricing={"input_cache_hit": 0.025, "input_cache_miss": 3.0, "output": 6.0},
    )

    assert secret not in repr(runtime)
    assert secret not in json.dumps(runtime.public_config())


def test_dry_run_does_not_need_database_or_network():
    result = evaluator.run_dry_run(DATASET_PATH)

    assert result["ok"] is True
    assert result["cases_validated"] == 7
    assert "no database or network access" in result["checks"]
