#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
FLASK_DIR="$ROOT_DIR/Flask"
START_SCRIPT="$FLASK_DIR/start_backend.sh"
TEMPLATE="$SCRIPT_DIR/ensure-backend.user.service.template"
USER_SYSTEMD_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
SERVICE_FILE="$USER_SYSTEMD_DIR/ensure-backend.service"
PYTHON_BIN_DIR="$(dirname "$(command -v python3)")"

if [[ ! -x "$START_SCRIPT" ]]; then
  echo "[ENSURE] start script is not executable: $START_SCRIPT" >&2
  exit 1
fi

mkdir -p "$USER_SYSTEMD_DIR"

sed \
  -e "s#__FLASK_DIR__#$FLASK_DIR#g" \
  -e "s#__PYTHON_BIN_DIR__#$PYTHON_BIN_DIR#g" \
  -e "s#__START_SCRIPT__#$START_SCRIPT#g" \
  "$TEMPLATE" > "$SERVICE_FILE"

systemctl --user daemon-reload
systemctl --user enable ensure-backend.service
systemctl --user restart ensure-backend.service

echo "[ENSURE] installed user service: $SERVICE_FILE"
echo "[ENSURE] status: systemctl --user status ensure-backend.service"
echo "[ENSURE] logs:   journalctl --user -u ensure-backend.service -f"
echo
echo "[ENSURE] For start at machine boot before login, run once:"
echo "sudo loginctl enable-linger $USER"
