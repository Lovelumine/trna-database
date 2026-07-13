# ENSURE Research Model Benchmark

This benchmark compares `mimo-v2.5-pro` and `deepseek-v4-pro` on the same
frozen ENSURE scientific evidence. It measures answer synthesis rather than
retrieval: every provider receives byte-for-byte equivalent questions, source
labels, and evidence excerpts.

Tracked inputs and code:

- `ensure_research_benchmark.json`: fixed questions, frozen `[S#]` sources,
  expected facts, model IDs, and provider-native CNY pricing snapshots.
- `../scripts/evaluate_research_models.py`: live runner, scorer, streaming
  latency collector, token/cost normalizer, and JSON/Markdown renderer.
- `../tests/test_research_model_eval.py`: offline scoring and secret-safety
  tests.

Runtime outputs are written under
`Flask/artifacts/research-model-eval/<run-id>/` and ignored by Git.

## Offline validation

The dry run validates all dataset references, generates deterministic perfect
answers, checks fact scoring and valid/invalid citations, and verifies the cost
formula. It performs no database access, network request, or artifact write.

```bash
/usr/soft/conda/bin/python Flask/scripts/evaluate_research_models.py --dry-run
/usr/soft/conda/bin/python -m pytest -q Flask/tests/test_research_model_eval.py
```

## Small live comparison

Run one fixed question against both providers:

```bash
/usr/soft/conda/bin/python Flask/scripts/evaluate_research_models.py --limit 1
```

Run the stable Engineered record pair explicitly:

```bash
/usr/soft/conda/bin/python Flask/scripts/evaluate_research_models.py \
  --case engineered-stable-record-pair-1206-1211
```

Run all cases:

```bash
/usr/soft/conda/bin/python Flask/scripts/evaluate_research_models.py
```

Useful filters:

```bash
# One provider only
/usr/soft/conda/bin/python Flask/scripts/evaluate_research_models.py \
  --provider xiaomi --limit 2

# Explicit run directory and timeout
/usr/soft/conda/bin/python Flask/scripts/evaluate_research_models.py \
  --run-id manual-comparison-01 --timeout 180
```

The live command exits with status `2` if any model request fails, but it still
writes the successful and failed result records for diagnosis.

## Metrics

- **Accuracy**: weighted expected-fact coverage using frozen keywords and
  alternatives. This is deterministic, but scientific expert review remains
  the final authority.
- **`[S#]` citation validity**: valid supplied citation occurrences divided by
  all citation occurrences. No citations scores zero when citations are
  required.
- **Source coverage**: required source labels cited at least once.
- **Fact citation support**: matched facts with a nearby allowed citation.
- **TTFT**: seconds from request start to the first non-empty answer-content
  delta. Reasoning-only deltas do not count.
- **Total latency**: seconds through stream completion.
- **Tokens**: provider-reported streaming usage where available. When absent,
  the record is explicitly marked `estimated` (or `api+estimated`).
- **Estimated cost**: cache-hit input, cache-miss input, and output tokens
  multiplied by the provider's published CNY-per-million-token prices.

No currency conversion is performed. Both V4 Pro and MiMo V2.5 Pro pricing in
this snapshot is recorded directly in CNY from the provider pages:

- Xiaomi: <https://mimo.mi.com/docs/zh-CN/price/pay-as-you-go>
- DeepSeek: <https://api-docs.deepseek.com/zh-cn/quick_start/pricing>

## Credential safety

Live credentials and base URLs are loaded with a read-only `SELECT` from the
existing backend `app_settings` rows. The runner deliberately does not call
`create_app()` or settings helpers that can create defaults.

The API keys exist only inside in-memory provider runtime objects. They are not
printed or placed in result dictionaries. Before JSON or Markdown is written,
the runner rejects output containing either an exact loaded key or a key-like
`sk-...`/`tp-...` token. Do not pass credentials as CLI arguments or add them to
the benchmark dataset.

## Scope and maintenance

The frozen-evidence design makes provider comparison reproducible and isolates
model behavior. It does not measure ENSURE retrieval quality or the complete
multi-round `/chat/api/chat_message` workflow. Use a separate end-to-end suite
for those concerns.

When changing a case, verify its provenance against the referenced tracked
document or stable database row, increment the benchmark version when meaning
changes, and rerun both dry-run commands above. Never silently replace a source
excerpt with a newer live count: add a new versioned case instead.
