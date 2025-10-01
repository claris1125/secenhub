#!/usr/bin/env bash
set -euo pipefail
# Ubuntu 22.04 minimal setup
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip

# create venv in current project directory
DIR="$(cd "$(dirname "$0")/.."; pwd)"
cd "$DIR"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install fastapi "uvicorn[standard]"

echo "------------------------------------------------------"
echo "Install done."
echo "To run development server:"
echo "  cd $DIR"
echo "  export SCENE_TOKEN=changeme"
echo "  venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8080"
echo "Open http://localhost:8080/docs and open viewer.html"
echo "------------------------------------------------------"
