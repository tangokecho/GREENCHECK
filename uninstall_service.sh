#!/bin/bash
set -euo pipefail

SERVICE_NAME="tri-core-autogen.service"
USER_SYSTEMD_DIR="$HOME/.config/systemd/user"
SERVICE_FILE="$USER_SYSTEMD_DIR/$SERVICE_NAME"

systemctl --user disable --now "$SERVICE_NAME" || true
rm -f "$SERVICE_FILE"
systemctl --user daemon-reload

echo "Service $SERVICE_NAME uninstalled and stopped."
