# Deployment Notes

Verified and deployed on 2026-07-14 from commit `ce3f1ba`.

## Frontend

The ENSURE frontend is deployed in two places. Both deployments serve the same
`trna.lumoxuan.cn` build and contain these entry files:

- `index.html`
- `admin.html`
- `help.html`

Primary frontend host:

- Host: `223.82.75.76`
- Path: `/www/wwwroot/trna.lumoxuan.cn`

Secondary frontend host:

- Host: `43.131.52.172`
- OS: `Ubuntu 24.04 LTS`
- User: `ubuntu`
- Path: `/www/wwwroot/trna.lumoxuan.cn`

The local build and both frontend origins matched during verification:

- `index.html`: `1d51cdfc10c6637c2bc89dfaf601953f0b5a9442d556dbc5cd1abcd8c2e0d482`
- `admin.html`: `dd9b6a467599699de2f21a2f2cab5800cf24e98b162957be5d9be68260d77bf6`
- `help.html`: `edf69130a4be54d76c5fbe7c4ab70d92ab1776f33b2f665db13c1d62d03f4401`

The current deployments retain immediately restorable previous directories:

- Primary: `/www/wwwroot/trna.lumoxuan.cn.backup-20260714-225016`
- Secondary: `/www/wwwroot/trna.lumoxuan.cn.backup-20260714-230114`

## Backend

The ENSURE Flask backend runs only on the primary host.

- Host: `223.82.75.76`
- Hostname: `yingying-B660M-GAMING-D4`
- Path: `/home/yingying/Documents/trna-database/Flask`
- User service: `ensure-backend.service` (manage with `systemctl --user`)
- Bind: `0.0.0.0:8010`
- Health check: `http://127.0.0.1:8010/health`
- Start command: `Flask/start_backend.sh --no-install --server gunicorn --host 0.0.0.0 --port 8010`
- Active AI provider: Xiaomi MiMo (`mimo-v2.5-pro`)
- Automatic provider chain: official Xiaomi MiMo, then a configured
  MiMo-compatible relay, then DeepSeek (`deepseek-v4-pro`). Fallback is limited
  to retryable provider, transport, or protocol failures; configuration and
  non-retryable request errors stop instead of being silently masked.

The user unit is active and enabled with `Restart=always`. Host-level user
linger is enabled for `yingying` (`loginctl show-user yingying -p Linger`
returns `Linger=yes`), so the user service can start after a cold boot without
waiting for an interactive login.

The secondary host `43.131.52.172` had no `8010` listener and no ENSURE
Flask/Gunicorn process during verification.

## AI assistant release verification

- Anonymous visitors receive a signed, `HttpOnly`, `Secure`, `SameSite=Lax`
  identity cookie. Browser-local chat keys are scoped by the derived storage
  namespace, and chat IDs cannot be read from another visitor identity.
- Internal model tool markup and raw SQL are rejected before rendering or
  browser persistence. Audio and text clients only persist final content
  events, not draft or tool events.
- The full public RAG path returns structured, linked sources with inline
  `[S1]` citations and does not expose internal tool markup or raw SQL.
- The relay reports `mimo-v2.5` and `mimo-v2.5-pro` through an
  OpenAI-compatible API. Non-streaming, streaming, and MiMo Thinking requests
  passed. A production smoke request observed the official endpoint return
  HTTP 402, then completed through the relay with sanitized execution metadata
  (`xiaomi` / `xiaomi_relay`) and no endpoint, credential, or error detail in
  the browser payload.
- Streaming fallback is allowed only before the first visible token. Shared
  stage deadlines cover raw SSE events, and critic provenance is used only
  when the critic's revision actually becomes the final answer.
- Backend tests: `119 passed`.
- Frontend production build completed successfully (`2925` modules).
- Public health, identity, chat-open, home, and six primary application routes
  returned HTTP 200. All nine entry-page JS/CSS assets returned HTTP 200 and
  matched on both frontend origins.
- Independent Chrome profiles received different anonymous cookies and storage
  namespaces. Their scoped localStorage keys did not overlap; cross-visitor
  access to a signed chat ID returned HTTP 404. Desktop (1440 px), iPad
  (820 x 1180 px), and mobile (390 x 844 px) AI pages mounted in both light
  and dark themes without horizontal overflow or console errors.

## Secrets

Operational secrets are kept in ignored environment files or the backend
`app_settings` database table. LLM API keys are redacted from admin audit
before/after JSON. The MiMo relay endpoint and key use hidden settings that are
not returned by the administrator settings API. Never commit or expose them to
frontend code. Because the relay is a third-party compatible service, it only
receives prompts, conversation context, and retrieved evidence when the
official MiMo endpoint has first failed with a retryable error.
