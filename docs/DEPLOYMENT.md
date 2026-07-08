# Deployment Notes

Verified on 2026-07-08.

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

- `index.html`: `aff1f4ccb4162a5909bf0cad7a9d7947a872396cf0825d8a864ad930fc861eb5`
- `admin.html`: `067c27373160bff5e4990dbce6f0c67f3cf11f17ce4b39755e963f0ea07759be`
- `help.html`: `e9fffc4b2c768996c89b7cd4a18e21cb3b5d9d7f13dbed84c5dc049fbfcff70a`

## Backend

The ENSURE Flask backend runs only on the primary host.

- Host: `223.82.75.76`
- Hostname: `yingying-B660M-GAMING-D4`
- Path: `/home/yingying/Documents/trna-database/Flask`
- Service: `ensure-backend.service`
- Bind: `0.0.0.0:8010`
- Health check: `http://127.0.0.1:8010/health`
- Start command: `Flask/start_backend.sh --no-install --server gunicorn --host 0.0.0.0 --port 8010`

The secondary host `43.131.52.172` had no `8010` listener and no ENSURE
Flask/Gunicorn process during verification.

## Local Secrets

Operational secrets and SSH passwords are kept in local ignored `.env` files.
Do not commit them.
