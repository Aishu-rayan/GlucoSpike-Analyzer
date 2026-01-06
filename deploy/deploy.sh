#!/bin/bash
set -e

PROJECT_DIR="/home/sreenivasanac/projects/GlucoSpike-Analyzer"
FRONTEND_DIR="$PROJECT_DIR/frontend"
BACKEND_DIR="$PROJECT_DIR/backend"
DEPLOY_DIR="$PROJECT_DIR/deploy"
WEB_ROOT="/var/www/glucoguide"

echo "=== GlucoGuide Deployment Script ==="

# Check if .env exists
if [ ! -f "$DEPLOY_DIR/.env" ]; then
    echo "ERROR: $DEPLOY_DIR/.env not found!"
    echo "Please copy .env.example to .env and configure your OPENAI_API_KEY"
    exit 1
fi

# Build Frontend
echo ""
echo "=== Building Frontend ==="
cd "$FRONTEND_DIR"
npm install
npm run build

# Deploy frontend to web root
echo ""
echo "=== Deploying Frontend to $WEB_ROOT ==="
sudo mkdir -p "$WEB_ROOT"
sudo rm -rf "$WEB_ROOT"/*
sudo cp -r dist/* "$WEB_ROOT/"
sudo chown -R www-data:www-data "$WEB_ROOT"

# Setup Backend
echo ""
echo "=== Setting up Backend ==="
cd "$BACKEND_DIR"

# Create venv if not exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Install dependencies
echo "Installing Python dependencies..."
./venv/bin/pip install -r requirements.txt

# Setup systemd service
echo ""
echo "=== Setting up Systemd Service ==="
sudo cp "$DEPLOY_DIR/glucospike.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable glucospike
sudo systemctl restart glucospike

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Service status:"
sudo systemctl status glucospike --no-pager

echo ""
echo "Next steps (if first deployment):"
echo "1. Get SSL certificate:"
echo "   sudo certbot certonly --webroot -w /var/www/certbot -d gluco-guide.pragnyalabs.com"
echo ""
echo "2. Reload nginx:"
echo "   sudo nginx -t && sudo systemctl reload nginx"