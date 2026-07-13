# Deployment Notes

Verified and deployed on 2026-07-13.

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

The entry files matched during verification:

- `index.html`: `183b2e650ae1a338a0d48607f84252b23d0d0f58b92ad2f2f87f7b95088ed803`
- `admin.html`: `498bb392a156220fb427d26c8b9d46517d08d07cb02fccccea8b4e23e04c09cf`
- `help.html`: `1b417266073e709944b83b7dbdc4b37fb56288120430b731bfc4e19492b19733`

The 2026-07-13 MiMo deployment used stamp `20260713T161734Z`. Each frontend host
keeps both an immediately restorable previous directory and a compressed backup
under `/www/wwwroot/.ensure-backups/`.

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
- Rollback provider retained: DeepSeek (`deepseek-v4-pro`)

The user unit is active and enabled with `Restart=always`. Host-level user
linger is enabled for `yingying` (`loginctl show-user yingying -p Linger`
returns `Linger=yes`), so the user service can start after a cold boot without
waiting for an interactive login.

The secondary host `43.131.52.172` had no `8010` listener and no ENSURE
Flask/Gunicorn process during verification.

## Secrets

Operational secrets are kept in ignored environment files or the backend
`app_settings` database table. LLM API keys are redacted from admin audit
before/after JSON. Never commit or expose them to frontend code.
