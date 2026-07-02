# Deployment Notes

Verified on 2026-07-02.

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

- `index.html`: `f51682a5edbe7e9c9f8ac7944d6a2b71b070c2981a692224e02607b95e82d8d3`
- `admin.html`: `da12e973cb7b074c161cba828383805ec61b1f7bca6e71d40045357151c57d59`
- `help.html`: `a6f4da180f6283e19a5a03ac67a53fbee9fe6280e9460b18a4f767a3784186e8`

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
