#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="/home/sreenivasanac/projects/GlucoSpike-Analyzer"
WEB_ROOT="/var/www/glucoguide"

echo "[deploy] repo: ${REPO_DIR}"
cd "${REPO_DIR}"

export PATH="$HOME/.local/bin:$PATH"

echo "[deploy] git fetch/pull"
git fetch --prune
git checkout main
git pull --ff-only

# Runtime sqlite DB changes at runtime and should not block deployments.
git reset -- backend/app.db 2>/dev/null || true

echo "[deploy] frontend build"
cd frontend
npm ci
npm run build

echo "[deploy] publish frontend -> ${WEB_ROOT}"
sudo /bin/mkdir -p "${WEB_ROOT}"
sudo /bin/rm -rf "${WEB_ROOT}"/*
sudo /bin/cp -r dist/* "${WEB_ROOT}/"
sudo /bin/chown -R www-data:www-data "${WEB_ROOT}"

echo "[deploy] backend deps"
cd "${REPO_DIR}/backend"
if [ ! -d venv ]; then
  python3 -m venv venv
fi
./venv/bin/pip install -U pip
./venv/bin/pip install -r requirements.txt

echo "[deploy] restart backend"
sudo /usr/bin/systemctl restart glucospike

echo "[deploy] validate+reload nginx"
sudo /usr/sbin/nginx -t
sudo /usr/bin/systemctl reload nginx

echo "[deploy] done"
