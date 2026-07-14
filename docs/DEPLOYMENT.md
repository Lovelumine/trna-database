# Deployment Notes

Verified and deployed on 2026-07-14 from commit `6ebe405`.

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

- `index.html`: `d88e986a9078d7c09b570412a685c8ca2a1f93aede2c9a670fd59d5898b25816`
- `admin.html`: `dd9b6a467599699de2f21a2f2cab5800cf24e98b162957be5d9be68260d77bf6`
- `help.html`: `d09e691720d2a3d19afc4e8a16ab6b76e8a3ed666a4299b248257110617f771b`

The current deployments retain immediately restorable previous directories:

- Primary: `/www/wwwroot/trna.lumoxuan.cn.backup-20260714-182239`
- Secondary: `/www/wwwroot/trna.lumoxuan.cn.backup-20260714-182320`

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
- Automatic provider fallback: DeepSeek (`deepseek-v4-pro`) when MiMo returns a
  retryable provider or network error

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
- MiMo credential and full public RAG-path checks passed against the official
  Xiaomi endpoint without invoking the fallback. The deployed RAG response
  contained four structured, linked sources, inline `[S1]` citations, and no
  internal tool or SQL leakage.
- Backend tests: `86 passed`.
- Frontend production build completed successfully (`2925` modules).
- Public health, identity, chat-open, home, and six primary application routes
  returned HTTP 200. All nine entry-page JS/CSS assets returned HTTP 200 and
  matched on both frontend origins.
- Independent Chrome profiles received different anonymous cookies and storage
  namespaces. Their scoped localStorage keys did not overlap; cross-visitor
  access to a signed chat ID returned HTTP 404. Desktop (1440 px) and mobile
  (390 x 844 px) AI pages mounted in both light and dark themes without
  horizontal overflow or console errors.

## Secrets

Operational secrets are kept in ignored environment files or the backend
`app_settings` database table. LLM API keys are redacted from admin audit
before/after JSON. Never commit or expose them to frontend code.
