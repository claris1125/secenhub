#!/usr/bin/env bash
set -euo pipefail
# Create a systemd service for SceneHub
DIR="$(cd "$(dirname "$0")/.."; pwd)"
USER_NAME="${SUDO_USER:-$USER}"

# Ensure venv exists
if [ ! -x "$DIR/venv/bin/uvicorn" ]; then
  echo "venv not found: $DIR/venv. Run scripts/install.sh first."
  exit 1
fi

# Create environment file
sudo mkdir -p /etc/default
if [ ! -f /etc/default/scenehub ]; then
  echo 'SCENE_TOKEN=changeme' | sudo tee /etc/default/scenehub >/dev/null
  echo "Created /etc/default/scenehub (edit to change token)"
fi

# Write service
sudo tee /etc/systemd/system/scenehub.service >/dev/null <<EOF
[Unit]
Description=SceneHub (FastAPI)
After=network-online.target

[Service]
User=$USER_NAME
WorkingDirectory=$DIR
EnvironmentFile=/etc/default/scenehub
ExecStart=$DIR/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8080 --proxy-headers
Restart=always
RestartSec=2

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now scenehub
echo "SceneHub service started. Check: sudo systemctl status scenehub"
echo "API: http://<this_host>:8080/docs"
