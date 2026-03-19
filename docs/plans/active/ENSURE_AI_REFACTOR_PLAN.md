# ENSURE AI Refactor Plan

## 1. Purpose

This document is the detailed, AI-only implementation plan for the ENSURE repository.

It is intentionally scoped to the AI assistant subsystem and excludes broad site-wide refactor ideas unless they directly affect AI behavior.

The goals are:

1. define the current AI architecture precisely;
2. record the current MySQL-backed AI configuration baseline;
3. propose a safe staged refactor for multi-round retrieval and workflow control;
4. keep changes constrained to AI-specific backend, admin, and frontend surfaces;
5. avoid accidental edits to unrelated data pages or public site structure.

## 2. Scope

This plan covers only the AI subsystem:

- main full-page AI assistant;
- floating bot assistant;
- shared chat transport for the main AI surfaces;
- Flask chat pipeline;
- MySQL-backed AI settings in `app_settings`;
- admin configuration UI for AI runtime and AI workflow.

This plan does **not** attempt to redesign:

- audio/video assistant UI or subtitle-context assembly;
- public data browsing pages;
- download system;
- help site architecture;
- therapeutics page data model;
- BLAST/search behavior outside the main AI workflow.

## 3. AI Code Surfaces

### 3.1 Frontend AI Surfaces

#### Full-page AI

- `src/views/AIYingying/AIYingying.vue`
- `src/views/AIYingying/ChatBox/ChatBox.vue`

Responsibilities:

- conversation list/session switching;
- usage note gating;
- model selection;
- full conversation rendering;
- evidence rendering;
- regenerate/edit flows.

#### Floating bot AI

- `src/bot/BotComponent.vue`

Responsibilities:

- draggable floating chat launcher;
- shared assistant access from non-AI public pages;
- model and conversation switching in the widget;
- progress card and evidence rendering.

### 3.2 Shared Frontend Chat Transport

The main transport is:

- `src/utils/useChat.ts`

Current capabilities already present:

- chat session initialization;
- stream abort/stop;
- progress state;
- tool trace list;
- streaming content assembly;
- optional model override per request;
- client-provided chat history for regeneration/edit flows.

Important existing SSE handling:

- `type=status`
- `type=tool`
- default content events

This is critical because the future multi-round retrieval design can reuse the current transport rather than requiring a new streaming protocol.

### 3.3 Backend AI Surfaces

Primary backend files:

- `Flask/app/routes.py`
- `Flask/app/settings_store.py`
- `Flask/config.py`
- `Flask/app/models.py`

Current chat endpoints:

- `GET /chat/api/models`
- `GET /chat/api/application/profile`
- `GET /chat/api/open`
- `POST /chat/api/title`
- `POST /chat/api/chat_message/<chat_id>`

### 3.4 Admin AI Surfaces

Current admin configuration code:

- `src/views/admin/AdminWorkspace.vue`
- `src/utils/admin.ts`
- `Flask/app/routes.py`
- `Flask/app/settings_store.py`

Current admin AI settings cover:

- active provider;
- active model;
- timeout;
- max messages;
- system prompt;
- DeepSeek base URL/default model/API key/model list;
- Ollama base URL/default model/model list.

## 4. Current MySQL AI Configuration Baseline

This section is based on reading the live configured MySQL-backed `app_settings` through the Flask app context.

### 4.1 Current `app_settings` Snapshot

Observed total setting count:

- `15`

Observed AI-related or adjacent keys:

- `llm_active_model`
- `llm_active_provider`
- `llm_deepseek_api_key`
- `llm_deepseek_base_url`
- `llm_deepseek_default_model`
- `llm_deepseek_models_json`
- `llm_max_messages`
- `llm_ollama_base_url`
- `llm_ollama_default_model`
- `llm_ollama_models_json`
- `llm_system_prompt`
- `llm_timeout`
- `table_column_label_overrides_json`
- `table_default_visible_columns_json`
- `table_media_field_config_json`

### 4.2 Current Effective LLM Runtime Snapshot

Observed current values in MySQL:

- active provider: `deepseek`
- active model: `deepseek-chat`
- timeout: `120`
- max messages: `20`
- DeepSeek base URL: `https://api.deepseek.com`
- DeepSeek default model: `deepseek-chat`
- DeepSeek model list: `["deepseek-chat", "deepseek-reasoner"]`
- Ollama default model: `qwen3:32b`
- Ollama model list: `["qwen3:32b", "gemma3:27b"]`
- Ollama base URL in DB: empty string
- system prompt length: `1973` characters
- DeepSeek API key exists in DB

Key observation:

- there are **no** `ai_*` workflow configuration keys yet.

That means the current system can switch providers/models from MySQL, but the retrieval workflow itself is still governed by hard-coded backend config and logic rather than admin-tunable workflow settings.

### 4.3 Current AI Retrieval Coverage Snapshot

Observed docs available under `public/docs` at top level:

- `9` files

Observed core table counts relevant to AI retrieval:

- `coding_variation_cancer = 16225`
- `coding_variation_genetic_disease = 380`
- `Engineered_sup_tRNA = 1129`
- `nonsense_sup_rna = 52`
- `frameshift_sup_trna = 34`
- `function_and_modification = 268`
- `aars_recognition = 102`
- `ef_tu = 60`
- `pmid_article_info_extended = 65`
- `engineered_sup_trna_perpos_counts = 312`

Implication:

- the AI already has a non-trivial structured retrieval surface across both curated database tables and site docs;
- refactor work should focus on orchestration quality rather than inventing new sources first.

## 5. Current AI Runtime Architecture

### 5.1 Runtime Selection

The backend currently resolves runtime through:

- `get_llm_settings(include_secrets=True)` in `Flask/app/settings_store.py`
- `_get_llm_runtime()` in `Flask/app/routes.py`

Current design properties:

- provider is inferred from current admin setting or requested model;
- requested model is allowed only if present in the stored model options;
- runtime payload is reconstructed per request.

### 5.2 Tool Planning and Retrieval

The backend already includes:

- tool planner prompt;
- tool sanitization;
- tool execution cache;
- signals/counters from retrieval;
- evidence gate;
- RAG document and table retrieval;
- PubMed search/fetch flow;
- optional repo/code search tools.

Important current functions:

- `_plan_tools`
- `_execute_tool_plan`
- `_execute_tool_cached`
- `_run_tool_pipeline`
- `_evidence_gate`
- `_rag_retrieve`

### 5.3 Answer Generation and Critique

The backend already includes:

- `_build_answer_messages`
- `_generate_answer`
- `_critique_answer`
- `_check_answer_pmids`
- `_remove_invalid_pmids`

Current limitation:

- the orchestration is not yet explicitly organized as a clean round-based retrieval workflow with admin-configurable stopping rules.

### 5.4 Current Streaming Behavior

Current frontend already supports process streaming well.

Current backend stream semantics:

- emit `status`
- emit `tool`
- emit answer `content`
- emit evidence payload at the end

This means the future design should preserve SSE and improve orchestration, not replace streaming.

## 6. Current AI Product Behavior

### 6.1 What the AI Already Does Well

- retrieves from ENSURE docs and public site materials;
- retrieves table rows/stats from MySQL;
- can include PubMed search/fetch;
- keeps conversation history;
- exposes evidence to the frontend;
- exposes tool activity to the frontend;
- allows model selection from UI;
- stores runtime provider/model configuration in MySQL via admin.

### 6.2 Current Product Gaps

The main problems are orchestration and control, not total capability absence.

Observed gaps:

- no MySQL-backed AI workflow settings;
- no explicit `ai_max_retrieval_rounds`;
- no distinct retrieval judge role;
- no explicit stop-reason surface;
- no admin control for retrieval depth;
- answer refinement logic exists, but the workflow is still not a first-class multi-round planner/judge loop;
- no workflow observability panel in admin.

## 7. AI Refactor Objectives

The AI refactor should achieve the following:

1. store workflow control in MySQL-backed settings;
2. let admins tune retrieval rounds and stopping rules;
3. convert retrieval into explicit rounds;
4. use a retrieval judge to decide whether to deepen evidence;
5. preserve SSE-based progress streaming;
6. emit only the final mature answer text when configured to do so;
7. keep final critic and PMID validation as post-retrieval safety checks;
8. avoid touching unrelated public data page logic.

## 8. Non-Goals

The following are explicitly out of scope for the AI refactor:

- rewriting `tRNAtherapeutics` data flow;
- redesigning the help site;
- migrating all public pages to one table abstraction;
- removing the lightweight sequence search service;
- replacing Flask sessions/admin auth;
- broad UI redesign across the public site.

## 9. Proposed Target AI Architecture

### 9.1 High-Level Flow

Target flow:

1. receive user question
2. initialize runtime and chat history
3. run round 1 retrieval
4. retrieval judge checks sufficiency
5. if insufficient, run round 2 retrieval
6. repeat until stop condition
7. generate final answer
8. run final critic if enabled
9. validate PMIDs
10. return final answer and evidence package

### 9.2 Streaming Behavior

Target streaming rule:

- before final answer:
  - stream `status`
  - stream `tool`
  - optionally stream `judge`
- after retrieval converges:
  - stream final answer `content`
- at the end:
  - stream evidence package

Recommended default:

- `ai_stream_final_only = 1`

That matches the current product direction better than pushing incomplete first-pass answer text.

### 9.3 Separation of Roles

#### Retrieval Judge

Purpose:

- decide if the evidence is sufficient;
- identify what is missing;
- suggest next tool calls;
- determine whether the system should stop.

This is not the same as an answer critic.

#### Final Critic

Purpose:

- verify the final answer is supported by evidence;
- revise unsupported or speculative wording;
- help enforce PMID validity.

This role already partially exists and should be retained as a separate step.

## 10. MySQL Configuration Design

### 10.1 Storage Strategy

Continue using:

- table: `app_settings`
- model: `AppSetting`
- key/value storage pattern

Do **not** create a separate AI settings table in the first wave.

Reason:

- the project already has a working app-settings persistence path;
- admin UI and backend route patterns already exist;
- schema expansion is unnecessary for the first iteration.

### 10.2 New `app_settings` Keys

Recommended keys:

- `ai_workflow_enable`
- `ai_stream_final_only`
- `ai_max_retrieval_rounds`
- `ai_max_tool_steps_per_round`
- `ai_max_total_tool_steps`
- `ai_retrieval_judge_enable`
- `ai_retrieval_judge_model`
- `ai_retrieval_judge_threshold`
- `ai_allow_pubmed_deepen`
- `ai_allow_table_deepen`
- `ai_allow_doc_deepen`
- `ai_stop_on_no_new_evidence`
- `ai_stop_on_repeated_plan`
- `ai_final_critic_enable`

### 10.3 Default Values

Recommended defaults:

- `ai_workflow_enable = 1`
- `ai_stream_final_only = 1`
- `ai_max_retrieval_rounds = 2`
- `ai_max_tool_steps_per_round = 4`
- `ai_max_total_tool_steps = 12`
- `ai_retrieval_judge_enable = 1`
- `ai_retrieval_judge_model = ""`
- `ai_retrieval_judge_threshold = 0.80`
- `ai_allow_pubmed_deepen = 1`
- `ai_allow_table_deepen = 1`
- `ai_allow_doc_deepen = 1`
- `ai_stop_on_no_new_evidence = 1`
- `ai_stop_on_repeated_plan = 1`
- `ai_final_critic_enable = 1`

### 10.4 Hard Safety Limits

Even if admin settings are misconfigured, backend should enforce:

- maximum rounds hard cap: `5`
- maximum total tool steps hard cap: `30`
- judge threshold clamp: `0.0-1.0`

## 11. Backend Refactor Plan

### 11.1 Phase 1: Settings Support

Files:

- `Flask/app/settings_store.py`
- `Flask/app/routes.py`
- `src/utils/admin.ts`
- `src/views/admin/AdminWorkspace.vue`

Tasks:

- add default factories for `ai_*` keys;
- add `get_ai_workflow_settings()` helper;
- add `save_ai_workflow_settings()` helper;
- add admin GET/POST route for workflow settings;
- add admin frontend type and save/load methods;
- add admin form UI.

This phase should not change chat behavior yet.

### 11.2 Phase 2: Retrieval Judge

Files:

- `Flask/app/routes.py`

Tasks:

- add retrieval-judge prompt;
- add parser for judge JSON output;
- define normalized judge response shape:
  - `enough`
  - `coverage_score`
  - `missing_aspects`
  - `tool_calls`
  - `stop_reason`
- separate this from current final critic logic.

### 11.3 Phase 3: Multi-Round Orchestrator

Files:

- `Flask/app/routes.py`

Tasks:

- wrap retrieval pipeline in explicit round loop;
- enforce per-round and total step budgets;
- detect repeated tool plans;
- detect no-new-evidence condition;
- accumulate round trace;
- surface stop reason;
- only start final answer streaming when retrieval stops.

### 11.4 Phase 4: Final Critic Integration Cleanup

Files:

- `Flask/app/routes.py`

Tasks:

- keep final critic optional via setting;
- ensure final critic runs after retrieval convergence, not as a substitute for judge;
- keep PMID validation step after final answer generation;
- ensure final answer remains evidence-bounded.

## 12. Admin UI Refactor Plan

### 12.1 Current State

Current admin LLM section in `AdminWorkspace.vue` already includes runtime settings only.

Current fields:

- provider
- model
- timeout
- max messages
- DeepSeek settings
- Ollama settings
- system prompt

### 12.2 Target State

Keep two separate cards or sub-sections:

#### Model Runtime

Existing settings remain here:

- active provider
- active model
- timeout
- max messages
- provider-specific base URL/default model/model list
- system prompt

#### AI Workflow

New settings go here:

- workflow enabled
- stream final only
- max retrieval rounds
- max tool steps per round
- max total steps
- retrieval judge enabled
- retrieval judge model
- retrieval judge threshold
- allow PubMed deepen
- allow table deepen
- allow docs deepen
- stop on no new evidence
- stop on repeated plan
- final critic enabled

### 12.3 Save Strategy

Recommended API design:

- keep `/admin/api/llm_settings` for runtime only;
- add `/admin/api/ai_workflow_settings` for workflow only.

Reason:

- runtime settings and workflow settings have different responsibilities;
- mixing them into one payload will make auditing and UI maintenance harder.

### 12.4 Audit Logging

Workflow settings saves should generate audit records just like current LLM settings changes.

Recommended audit action:

- `update_ai_workflow_settings`

## 13. Frontend AI Refactor Plan

### 13.1 Shared Transport Changes

Primary file:

- `src/utils/useChat.ts`

Changes:

- keep current SSE transport;
- optionally recognize a future `judge` event type;
- preserve current `status/tool/content` compatibility;
- optionally store `round` and `stopReason` metadata for the session.

### 13.2 Full-Page AI UI

Primary file:

- `src/views/AIYingying/ChatBox/ChatBox.vue`

Changes:

- continue using loading card and tool activity list;
- optionally render round labels:
  - `Round 1`
  - `Round 2`
  - `Judge review`
- continue to keep the answer body clean and evidence collapsible;
- do not surface half-generated answer text if final-only streaming is enabled.

### 13.3 Floating Bot UI

Primary file:

- `src/bot/BotComponent.vue`

Changes:

- keep process card behavior aligned with the full-page AI;
- preserve regenerate/edit controls;
- avoid UI divergence between floating bot and full-page AI for workflow progress.

### 13.4 Out-of-Scope Compatibility

First-wave rule:

- do not modify `src/views/audio/AiAssistant/*` in this AI refactor;
- keep `/chat/api` event semantics backward compatible where practical;
- if backend behavior changes require adaptation, prefer a compatibility layer over an audio-assistant redesign.

## 14. Prompt Design Changes

### 14.1 Retrieval Judge Prompt Requirements

The retrieval judge prompt should require JSON only and should answer:

- whether the current evidence is enough;
- what factual dimensions are still missing;
- which tool calls should be executed next;
- whether further retrieval should stop.

Suggested output shape:

```json
{
  "enough": false,
  "coverage_score": 0.62,
  "missing_aspects": ["missing concrete examples", "missing PMID-backed evidence"],
  "tool_calls": [
    { "tool": "table_rows", "params": {} },
    { "tool": "pubmed_fetch", "params": {} }
  ],
  "stop_reason": ""
}
```

### 14.2 Final Critic Prompt Requirements

The final critic should remain focused on:

- unsupported claims;
- speculative wording;
- revision if possible;
- PMID consistency.

It should not decide retrieval depth.

## 15. Stop Conditions

The system should stop retrieval when any of the following is true:

- max retrieval rounds reached;
- max total tool steps reached;
- no new evidence was added in the latest round;
- retrieval judge proposed the same plan again;
- coverage score is above threshold;
- retrieval judge explicitly returns a stop reason;
- tool failures make additional retrieval non-productive.

Recommended first-release defaults:

- rounds: `2`
- per-round tool steps: `4`
- total steps: `12`

## 16. Data and Evidence Handling Rules

The AI refactor must preserve these rules:

- evidence must remain attached to the final answer;
- PMIDs cited in the answer must be validated against evidence;
- retrieval must remain bounded by the available ENSURE data and optional PubMed content;
- model/provider identity should continue to be hidden from user-facing assistant identity text;
- if evidence is insufficient, the assistant should say so explicitly rather than hallucinate.

## 17. Detailed File Impact List

### 17.1 Files to Change in Phase 1

- `Flask/app/settings_store.py`
- `Flask/app/routes.py`
- `src/utils/admin.ts`
- `src/views/admin/AdminWorkspace.vue`

### 17.2 Files to Change in Phase 2-4

- `Flask/app/routes.py`
- `src/utils/useChat.ts`
- `src/views/AIYingying/ChatBox/ChatBox.vue`
- `src/bot/BotComponent.vue`

### 17.3 Files to Leave Alone in First AI Wave

- `src/views/tRNAtherapeutics/tRNAtherapeutics.vue`
- `src/views/tRNAtherapeutics/tRNAtherapeutics-1.vue`
- `src/views/tRNAtherapeutics/ExpandedRow.vue`
- `src/views/tRNAtherapeutics/expandedRowLogic.ts`
- `src/views/help/help.vue`

## 18. API Contract Plan

### 18.1 New Admin Workflow Routes

Recommended:

- `GET /admin/api/ai_workflow_settings`
- `POST /admin/api/ai_workflow_settings`

### 18.2 Chat SSE Compatibility

Current events to preserve:

- `status`
- `tool`
- `content`
- `evidence`
- `error`

Optional new event:

- `judge`

If `judge` is added, frontend should treat it as additive, not breaking.

## 19. Validation Checklist

### 19.1 After Phase 1

- admin login still works;
- current LLM settings still load and save;
- new AI workflow settings load and save;
- settings persist in MySQL `app_settings`;
- audit log records workflow changes.

### 19.2 After Phase 2-4

- `/chat/api/models` still works;
- `/chat/api/application/profile` still works;
- `/chat/api/open` still works;
- main AI page still streams process updates;
- floating bot still streams process updates;
- final answer appears once retrieval converges;
- evidence still appears at the end;
- PMIDs are still validated.

### 19.3 Regression Checks

- no change to therapeutics pages;
- no change to generic table page loading;
- no change to help entrypoint routing;
- no change to admin auth/session behavior;
- no breakage of lightweight search mode.

## 20. Rollout Order

Recommended implementation order:

1. Phase 1: MySQL workflow settings and admin UI
2. Phase 2: retrieval judge
3. Phase 3: multi-round backend orchestrator
4. Phase 4: final critic cleanup
5. Phase 5: frontend progress enrichment
6. docs synchronization

Do not combine all phases into one large change.

## 21. Success Criteria

The AI refactor is successful when:

- admins can configure AI workflow depth from the admin panel;
- workflow settings live in MySQL, not only `.env`;
- the AI can perform more than one retrieval round when needed;
- the system can stop automatically using explicit rules;
- progress remains streamable to the frontend;
- the user receives one mature final answer instead of unstable intermediate prose;
- evidence remains visible and citations remain bounded.

## 22. Immediate Next Implementation Step

The next code change should be **Phase 1 only**:

- add `ai_*` settings to `app_settings`;
- add admin routes and admin UI for workflow settings;
- do not alter `chat_message()` behavior yet.

This is the safest first move because it creates the AI control plane before changing AI orchestration logic.
