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

- `index.html`: `042760ffe42b79fa4ab1a2d9410638d0acb6b917bd7fcf6849e7cfecd32ebd17`
- `admin.html`: `d13dc6eaeeedb07344fc134bdbf51d7a4772e485a66b1d7080803e02c692d0c1`
- `help.html`: `ddf2ef0b3c94168a6b9226b1994c4e100aa5a9bfeb8d12b05a04e048db70e6d9`

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
