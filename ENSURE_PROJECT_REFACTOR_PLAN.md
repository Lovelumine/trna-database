# ENSURE Project Refactor Plan

## 1. Document Purpose

This document is the pre-change engineering plan for the ENSURE repository.

The goal is to:

1. capture a concrete understanding of the current codebase before making changes;
2. define the boundaries of future refactors;
3. plan the next round of AI assistant and platform improvements without breaking existing flows;
4. force all future changes to follow an agreed impact map instead of ad hoc edits.

This document is intentionally detailed because the repository is not a single, uniform application. It is a mixed system with:

- multiple frontend entry points;
- a full Flask backend;
- a standalone lightweight sequence search service;
- public user pages plus a separate admin SPA;
- legacy and newer data access patterns living side by side;
- AI features that already span multiple frontend surfaces.

## 2. Reading Scope

This plan is based on reading the first-party application source across the repository, with emphasis on the runtime code paths that affect production behavior.

Reviewed source areas:

- `src/main.ts`
- `src/App.vue`
- `src/help-main.ts`
- `src/admin-main.ts`
- `src/views/**`
- `src/utils/**`
- `src/components/**`
- `src/bot/**`
- `Flask/app/**`
- `Flask/config.py`
- `Flask/wsgi.py`
- `Flask/scripts/**`
- `tools/data-prep/**`
- `vite.config.js`
- `README.md`
- `public/docs/98-API-Reference.md`

Excluded from refactor-source reading as implementation targets:

- `node_modules/**`
- `dist/**`
- `public/vendor/**`
- most static docs/media assets
- vendored visualization/runtime libraries such as `src/fornac/**` and `src/utils/tRNAviz/**`

These excluded areas are not ignored as artifacts, but they are not the primary sources for application architecture decisions.

## 3. Current Project Topology

### 3.1 Frontend Entry Points

The frontend is not one SPA. It is three separately mounted applications:

- Main site: `index.html` -> `src/main.ts`
- Help site: `help.html` -> `src/help-main.ts`
- Admin site: `admin.html` -> `src/admin-main.ts`

Implication:

- routing, layout, and state assumptions cannot be made globally across all pages;
- changing one entry does not automatically affect the others;
- admin/help traffic is intentionally separated from the public main app shell.

### 3.2 Main Public Site

The public site is mounted through `src/main.ts` and rendered through `src/App.vue`.

Important characteristics:

- the main router owns public routes such as home, disease/cancer, therapeutics, natural sup-tRNA, tRNA elements, display, download, AI Yingying, audio, and blast;
- `/help` is redirected to `help.html`;
- `/admin*` is redirected to `admin.html#...`;
- `App.vue` conditionally hides the global navbar/footer/floating bot on AI/admin/audio routes.

Implication:

- any cross-site layout refactor must preserve route-sensitive shell behavior;
- AI full-page and floating AI are intentionally different experiences.

### 3.3 Help Site

The help site is a dedicated frontend entry that renders markdown-based documentation from `/docs/...`.

Important characteristics:

- `src/help-main.ts` is its own router;
- `src/views/help/help.vue` loads markdown files dynamically;
- the help site also routes users back out to the main public site for non-help pages.

Implication:

- help content is part of the information architecture and is also reused by AI retrieval;
- changes to docs loading may affect both help UX and AI evidence quality.

### 3.4 Admin Site

The admin app is its own hash-router SPA.

Important characteristics:

- `src/admin-main.ts` uses `createWebHashHistory()`;
- route guard checks `/admin/api/me`;
- `src/views/admin/AdminWorkspace.vue` is the real admin control center;

Implication:

- future configuration UI should be placed in `AdminWorkspace.vue`, not built as a parallel admin surface;
- route redirection from main site to `admin.html` must remain intact.

### 3.5 Backend Topology

The repository backend is centered on the full Flask application under `Flask/`.

The full backend serves:

- table browsing;
- table statistics;
- downloads;
- AI chat APIs;
- admin APIs;
- media and docs administration;
- search and alignment;
- export status tracking.

Implication:

- `/search` should be treated as part of the main Flask API surface;
- refactors should keep search/alignment logic consistent with the rest of the platform backend.

### 3.6 Vite Proxy Topology

`vite.config.js` proxies the frontend to the backend for:

- `/search`
- `/search_table`
- `/table_rows`
- `/table_stats`
- `/table_fulltext_rebuild`
- `/download_table`
- `/download_table_status`
- `/download_bundle_status`
- `/chat/api`
- `/admin/api`
- `/engineered_sup_trna`

Implication:

- public pages are tightly coupled to backend path contracts;
- endpoint renames without a coordinated frontend update will break the site immediately in development and in same-origin deployment.

## 4. Current Data Access Patterns

The codebase currently contains more than one data access style.

### 4.1 Shared MySQL Table Pattern

The primary reusable table pattern is:

- `src/utils/useTableData.ts`
- `src/utils/useMysqlTableData.ts`
- backend `/table_rows`
- backend `/table_stats`

This is used for most table-driven pages and supports:

- pagination;
- text search;
- full-text fallback;
- sorting;
- filters;
- page prefetching;
- stats queries.

Implication:

- this is the preferred long-term public data page abstraction.

### 4.2 Special-Case Therapeutics Pattern

`src/views/tRNAtherapeutics/tRNAtherapeutics.vue` does not fully use the shared table abstraction.

It currently combines:

- a PMID article summary table from `pmid_article_info_extended`;
- a per-position chart from `engineered_sup_trna_perpos_counts`;
- lazy expanded-row fetches to `/search_table` for exact `PMID` lookup in `Engineered_sup_tRNA`;
- a child detail table component `tRNAtherapeutics-1.vue` that performs local filtering of the already-fetched row set.

Additional complexity:

- `tRNAtherapeutics-1.vue` has optional edit/create/delete behavior under `?edit=1`;
- it uses admin session/CSRF state even though it lives inside the public route tree.

Implication:

- this page is a mixed-mode page and must not be blindly rewritten into the shared generic table flow without first preserving its PMID-grouping and inline edit behavior.

### 4.3 Expanded Detail Pattern

`src/views/tRNAtherapeutics/ExpandedRow.vue` and `expandedRowLogic.ts` form a separate detail-view pattern:

- detailed ENSURE_ID display;
- conditional edit mode;
- alignment formatting;
- NGL CIF structure loading;
- deeper record rendering that is not represented as a generic table page.

Implication:

- expanded detail pages are not equivalent to list pages;
- future normalization should separate "list browsing" from "detail presentation" explicitly.

### 4.4 Display Page Status

`src/views/display/Display.vue` currently uses hard-coded example data for structure/sequence/modification rather than a live database fetch.

Implication:

- not every public route is already fully integrated into the live backend;
- refactor plans must account for partially implemented or placeholder pages.

## 5. Current AI Architecture

### 5.1 AI Surfaces

There are at least three AI-facing frontend experiences:

1. Full-page AI assistant: `src/views/AIYingying/**`
2. Floating bot assistant: `src/bot/BotComponent.vue`
3. Video subtitle assistant: `src/views/audio/AiAssistant/**`

They are not identical UIs, but they overlap in transport and backend usage.

### 5.2 Shared Chat Transport

The main public AI surfaces use `src/utils/useChat.ts`.

This transport already handles SSE event types:

- `status`
- `tool`
- `content`

It also tracks:

- per-session chat state;
- abort/cancel;
- tool activity list;
- progress detail;
- model selection.

Implication:

- the frontend is already compatible with process-streaming and tool-trace visualization;
- future AI workflow changes do not require a transport rewrite from scratch.

### 5.3 Backend AI Pipeline

The chat entrypoint is `Flask/app/routes.py` under `/chat/api/chat_message/<chat_id>`.

The current backend already contains these building blocks:

- initial RAG retrieval;
- tool planning;
- tool execution with caching;
- evidence gate logic;
- model runtime selection;
- optional PubMed flow;
- answer generation;
- answer critic;
- PMID validation;
- evidence packaging.

Implication:

- the backend already contains much of the logic needed for a multi-round retrieval workflow;
- the problem is orchestration and control, not total absence of capabilities.

### 5.4 AI Settings Storage

The current AI runtime configuration already uses MySQL-backed `app_settings` instead of only `.env`.

Existing examples:

- active provider;
- active model;
- timeout;
- max messages;
- system prompt;
- model lists;
- DeepSeek credentials.

Implication:

- future AI workflow configuration belongs in MySQL-backed settings too;
- `.env` should remain for infrastructure/bootstrap defaults, not day-to-day workflow tuning.

## 6. Administrative and Security Architecture

The admin backend uses:

- session-based login;
- role storage in session;
- CSRF token for write endpoints;
- audit logging;
- media asset tracking;
- app settings persistence.

Important implication:

- any public-page feature that conditionally uses admin write actions must preserve admin session and CSRF behavior;
- future admin-driven AI workflow editing should follow the same write protection model.

## 7. Documentation and Runtime Drift Already Present

The current repository already contains signs of drift between code, docs, and copy. These matter because future refactors should reduce drift rather than multiply it.

Examples:

- Home page text still mentions GPT-4o, while actual runtime is provider-configurable and currently oriented around Ollama/DeepSeek.
- `public/docs/98-API-Reference.md` lists chat profile details that do not exactly match the current code response shape.
- `Display.vue` is still example-driven.
- Some pages use the shared table abstraction, while others use custom fetches.

Implication:

- future work must include a documentation synchronization phase, not only code changes.

## 8. Constraints for Any Future Refactor

The following constraints are mandatory.

### 8.1 Must Not Break Multi-Entry Frontend

Do not:

- merge help/admin into the public router;
- assume one app-level state store exists for all entrypoints;
- rewrite route redirection without preserving `help.html` and `admin.html` behavior.

### 8.2 Must Not Force All Data Pages into One Pattern Too Early

Do not:

- convert `tRNAtherapeutics` to the generic table flow before feature parity exists;
- remove `/search_table` without replacing exact-match lazy expansion behavior;
- collapse expanded views into list-page logic.

### 8.3 Must Not Move AI Workflow Tuning Back into `.env`

Do not:

- store retrieval rounds, judge thresholds, or workflow flags only in environment variables;
- make admin-tunable AI behavior depend on redeploy-only config.

### 8.4 Must Preserve Lightweight Search Mode

Do not:

- remove or implicitly break the Flask `/search` contract;
- hard-assume MySQL/full Flask is always present for alignment workflows.

## 9. Refactor Goals

The future change program should aim to achieve the following, in order:

1. stabilize architecture understanding;
2. centralize runtime AI workflow control in MySQL-backed settings;
3. convert the AI assistant into an explicit multi-round retrieval workflow;
4. surface workflow control and observability in the admin UI;
5. reduce divergence across public data pages where safe;
6. synchronize docs and runtime behavior.

## 10. Planned Change Program

### Phase 0: Freeze and Documentation

Objective:

- create an agreed architecture baseline before touching business logic.

Tasks:

- keep this document as the source of truth for planned changes;
- add file-level impact notes before each implementation phase;
- avoid opportunistic cleanup outside agreed scope.

Deliverables:

- this planning document;
- explicit scope approval for Phase 1.

### Phase 1: AI Workflow Settings in MySQL

Objective:

- separate "model runtime settings" from "AI workflow orchestration settings".

Recommended storage approach:

- continue using `app_settings`;
- do not create a new table initially;
- add new keys under a clear namespace.

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

Expected code touch points:

- `Flask/app/settings_store.py`
- `Flask/app/routes.py`
- `src/utils/admin.ts`
- `src/views/admin/AdminWorkspace.vue`

Design rule:

- keep `.env` only as initial defaults/fallbacks;
- persist effective settings in MySQL.

### Phase 2: Backend AI Orchestrator Refactor

Objective:

- make the AI assistant explicitly round-based instead of implicitly mixing retrieval and answer generation in one pass.

Target workflow:

1. question intake
2. initial RAG retrieval
3. initial tool plan
4. execute tools for round 1
5. retrieval judge checks evidence sufficiency
6. if insufficient, execute round 2 retrieval
7. repeat until stop condition
8. generate final answer
9. optionally run final critic
10. emit evidence package

Important design decision:

- stream process events during retrieval rounds;
- stream final answer content only after retrieval has converged;
- do not expose half-baked first-pass answer text if `ai_stream_final_only` is enabled.

New backend responsibilities:

- round counter;
- total tool budget enforcement;
- repeated-plan detection;
- no-new-evidence detection;
- explicit judge result parsing;
- clean stop reason reporting.

Expected code touch points:

- `Flask/app/routes.py`

Secondary affected areas:

- `Flask/config.py` only for fallback defaults if needed;
- `public/docs/98-API-Reference.md` after behavior stabilizes.

### Phase 3: Retrieval Judge and Final Critic Separation

Objective:

- stop using one critic concept for two different jobs.

Retrieval Judge should decide:

- whether evidence is sufficient;
- which aspects are still missing;
- which tools should be called next;
- whether to stop.

Final Critic should decide:

- whether the final answer overclaims;
- whether citations/PMIDs are valid;
- whether the final wording needs revision.

Rationale:

- evidence sufficiency and answer correctness are related but not the same decision;
- separating them will simplify prompts, logs, and UI statuses.

Expected code touch points:

- `Flask/app/routes.py`

### Phase 4: Admin Workflow Control Panel

Objective:

- expose AI workflow configuration safely to admins.

Recommended UI structure in admin:

- keep existing `Model Runtime` section for provider/model/prompt/timeout;
- add a separate `AI Workflow` section for rounds, judge, stop conditions, tool budgets.

Recommended UI fields:

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

Expected code touch points:

- `src/views/admin/AdminWorkspace.vue`
- `src/utils/admin.ts`
- `Flask/app/routes.py`
- `Flask/app/settings_store.py`

### Phase 5: AI Frontend Status Enrichment

Objective:

- show more precise workflow progress without changing the basic SSE transport shape.

Existing frontend already supports:

- `status`
- `tool`
- `content`

Recommended additions:

- include round number in status text or payload;
- include stop reason in final metadata;
- optionally add a `judge` event type if status strings become overloaded.

Frontend files likely affected:

- `src/utils/useChat.ts`
- `src/views/AIYingying/ChatBox/ChatBox.vue`
- `src/bot/BotComponent.vue`
- optionally `src/views/audio/AiAssistant/useChat.ts`

### Phase 6: Public Data Page Normalization

Objective:

- reduce the inconsistency between generic table pages and custom pages where doing so is safe.

This phase must be conservative.

Recommended first actions:

- document which public pages use shared table hooks and which use custom fetches;
- normalize query parameter naming where possible;
- align error/loading behavior across pages.

Do not do in the first wave:

- rewrite `tRNAtherapeutics` into the generic table framework;
- remove local filtering or grouped PMID behavior;
- remove edit mode integration from `tRNAtherapeutics-1.vue`.

Candidate later tasks:

- extract a special reusable pattern for "grouped list + lazy detail table";
- centralize expanded-row fetch and cache behavior.

### Phase 7: Documentation Synchronization

Objective:

- make user-facing and developer-facing docs reflect actual runtime behavior.

Targets:

- `README.md`
- `public/docs/98-API-Reference.md`
- relevant help text in Home/AI copy/admin labels

Known sync items:

- current AI model/provider messaging
- chat profile response shape
- AI workflow control availability
- special behavior of therapeutics/detail pages if exposed to users/admins

## 11. File Impact Map

### High Priority Files

- `Flask/app/routes.py`
- `Flask/app/settings_store.py`
- `Flask/app/models.py`
- `src/views/admin/AdminWorkspace.vue`
- `src/utils/admin.ts`
- `src/utils/useChat.ts`
- `src/views/AIYingying/ChatBox/ChatBox.vue`
- `src/bot/BotComponent.vue`

### Medium Priority Files

- `src/views/AIYingying/AIYingying.vue`
- `src/views/audio/AiAssistant/useChat.ts`
- `Flask/config.py`
- `README.md`
- `public/docs/98-API-Reference.md`

### Watch Carefully but Do Not Rewrite Early

- `src/views/tRNAtherapeutics/tRNAtherapeutics.vue`
- `src/views/tRNAtherapeutics/tRNAtherapeutics-1.vue`
- `src/views/tRNAtherapeutics/ExpandedRow.vue`
- `src/views/tRNAtherapeutics/expandedRowLogic.ts`
- `src/views/display/Display.vue`

## 12. Proposed Stop Conditions for AI Retrieval

Default recommendations:

- `ai_max_retrieval_rounds = 2`
- `ai_max_tool_steps_per_round = 4`
- `ai_max_total_tool_steps = 12`
- hard upper cap on rounds = `5`

Stop when any of the following becomes true:

- max round count reached;
- max total tool count reached;
- no new evidence added in the last round;
- judge proposes a repeated tool plan;
- evidence sufficiency score exceeds threshold;
- tool calls fail repeatedly for the same evidence target.

## 13. Observability Requirements

Future AI refactor work must improve observability instead of hiding orchestration complexity.

Recommended logging/trace fields:

- chat id
- selected provider/model
- workflow settings snapshot
- round number
- tool calls issued
- tool calls completed
- tool cache hits
- stop reason
- final answer length
- evidence item count
- invalid PMIDs removed

Recommended admin-facing runtime snapshot:

- latest run count
- average rounds per answer
- average tool calls per answer
- most frequent stop reason
- PubMed deepen frequency

## 14. Test and Validation Plan

The repository currently does not expose an obvious automated frontend/backend test harness.

Observed current tooling:

- frontend scripts: `dev`, `build`, `preview`
- no visible `vitest`, `jest`, `pytest`, `playwright`, or `cypress` suite in normal app workflow

Implication:

- every implementation phase will need a manual verification checklist;
- if time permits, backend AI workflow tests should be added in a small targeted way rather than pretending a full test suite already exists.

Required validation per implementation phase:

### Backend AI Validation

- verify `/chat/api/application/profile`
- verify `/chat/api/open`
- verify `/chat/api/chat_message/<chat_id>` on simple factual question
- verify multi-round retrieval stops correctly
- verify evidence package is still returned
- verify PMIDs are validated correctly

### Admin Validation

- verify login/session still works
- verify AI workflow settings load from DB
- verify AI workflow settings save to DB
- verify CSRF protection still applies
- verify audit log records admin workflow changes

### Public Site Validation

- verify AI Yingying full page still opens and streams
- verify floating bot still works
- verify audio assistant still works
- verify therapeutics page still loads PMID table, chart, and expanded detail
- verify generic table pages still load through `/table_rows` and `/table_stats`

## 15. What Must Not Be Changed in the First Implementation Wave

The first implementation wave must not:

- redesign the entire UI;
- merge help/admin/main into one router;
- rewrite the therapeutics pages into generic table pages;
- remove the lightweight search service;
- migrate AI workflow settings to `.env`;
- touch vendored visualization code unless a bug proves it is required;
- attempt a broad TypeScript migration or composition API rewrite across unrelated files.

## 16. Recommended Execution Order

1. approve this document;
2. add MySQL-backed AI workflow settings;
3. add admin UI for those settings;
4. refactor backend AI orchestration into explicit rounds;
5. enrich SSE progress reporting;
6. synchronize docs;
7. only then consider data-page normalization.

## 17. Approval Gate Before Business Logic Changes

Before modifying runtime behavior, confirm:

- the `app_settings` storage contract for AI workflow keys is accepted;
- the admin UI location is accepted;
- the multi-round AI orchestration model is accepted;
- the therapeutics pages are explicitly marked as a protected special case;
- the lightweight search service is kept intact.

## 18. Immediate Next Step

The next step after this document should be:

- implement Phase 1 only;
- do not combine Phase 1 and Phase 2 in a single change;
- keep the first code diff limited to settings storage, admin API, and admin UI plumbing.

This sequencing minimizes risk and creates a safe control plane before any deeper AI behavior changes.
