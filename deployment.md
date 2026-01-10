# Deployment (gluco-guide.pragnyalabs.com)

This project is deployed with:

- **Frontend**: static build served by **nginx** from `/var/www/glucoguide`
- **Backend**: **systemd** service `glucospike` (uvicorn/FastAPI) on `127.0.0.1:8002`
- **TLS**: **certbot** (Let’s Encrypt)

## One-time server setup

### 0) Prerequisites

- Ubuntu/Debian host
- `nginx`
- `certbot`
- Node.js 18+
- Python 3.10+

### 1) Create a deploy user and permissions (recommended)

Goal: allow deployments without giving the CI user full sudo.

Run the following **on the server** (as a sudo-capable admin):

```bash
sudo adduser --disabled-password --gecos "" glucodeploy

# Web roots used by nginx/certbot
sudo mkdir -p /var/www/glucoguide /var/www/certbot
sudo chown -R glucodeploy:www-data /var/www/glucoguide /var/www/certbot
sudo chmod -R 2775 /var/www/glucoguide /var/www/certbot

# Allow deploy user to manage ONLY this service + reload nginx (no password)
# Note: keep this readable using Cmnd_Alias (sudoers is picky about line breaks).
sudo tee /etc/sudoers.d/glucodeploy-glucospike >/dev/null <<'EOF'
Cmnd_Alias GLUCOSPIKE_CMDS = \
  /bin/systemctl restart glucospike, \
  /bin/systemctl daemon-reload, \
  /bin/systemctl enable glucospike, \
  /bin/systemctl status glucospike, \
  /bin/systemctl reload nginx, \
  /usr/sbin/nginx -t

glucodeploy ALL=NOPASSWD: GLUCOSPIKE_CMDS
EOF
sudo chmod 440 /etc/sudoers.d/glucodeploy-glucospike

# Validate sudoers file
sudo visudo -cf /etc/sudoers.d/glucodeploy-glucospike
```

### 2) Configure app secrets on the server

The backend service reads production environment variables from:

`deploy/.env` (via systemd `EnvironmentFile` in `deploy/glucospike.service`)

For local development, use `backend/.env`.

Create it on the server:

```bash
cd /home/sreenivasanac/projects/GlucoSpike-Analyzer
cp .env.example deploy/.env
${EDITOR:-nano} deploy/.env
```

Contents:

```env
OPENAI_API_KEY=...
USDA_API_KEY=...
```

### 3) Install nginx config

Use the template from the repo:

`deploy/nginx/gluco-guide.pragnyalabs.com.conf.template`

```bash
cd /home/sreenivasanac/projects/GlucoSpike-Analyzer
sudo cp deploy/nginx/gluco-guide.pragnyalabs.com.conf.template /etc/nginx/sites-available/gluco-guide.pragnyalabs.com.conf
sudo ln -sf /etc/nginx/sites-available/gluco-guide.pragnyalabs.com.conf /etc/nginx/sites-enabled/gluco-guide.pragnyalabs.com.conf
sudo nginx -t && sudo systemctl reload nginx
```

If you need to refresh nginx config during/after deployment (only when the template changes):

```bash
cd /home/sreenivasanac/projects/GlucoSpike-Analyzer
sudo cp deploy/nginx/gluco-guide.pragnyalabs.com.conf.template /etc/nginx/sites-available/gluco-guide.pragnyalabs.com.conf
sudo nginx -t && sudo systemctl reload nginx
```

### 4) Issue TLS certificate (certbot)

```bash
sudo certbot certonly --webroot -w /var/www/certbot -d gluco-guide.pragnyalabs.com
sudo nginx -t && sudo systemctl reload nginx
```

## Deploy (manual)

Run:

```bash
cd /home/sreenivasanac/projects/GlucoSpike-Analyzer
./deploy/deploy.sh
```

Notes:

- `deploy/deploy.sh` currently uses `sudo` for:
  - writing to `/var/www/glucoguide`
  - installing/restarting the systemd unit
- With the `glucodeploy` setup above, you can reduce `sudo` usage to only `systemctl`/`nginx -t` by updating `deploy/deploy.sh` accordingly.

## Auto-deploy on merge to `main` (GitHub Actions)

Goal: on every push/merge to `main`, deploy to `https://gluco-guide.pragnyalabs.com/`.

### 1) Server requirements

- Repo is present at `/home/sreenivasanac/projects/GlucoSpike-Analyzer`
- `deploy/.env` exists with correct values
- SSH access for the deploy user (recommended: `glucodeploy`)

### 2) GitHub repo secrets

Add these secrets in GitHub → Settings → Secrets and variables → Actions:

- `DEPLOY_HOST`: server hostname/IP
- `DEPLOY_USER`: SSH username (e.g. `glucodeploy`)
- `DEPLOY_SSH_KEY`: private key for the deploy user

### 3) Workflow outline

Create `.github/workflows/deploy.yml` to:

1. Trigger on `push` to `main`
2. SSH to the server
3. `git fetch` and reset to `origin/main`
4. Run `./deploy/deploy.sh`

## Verify

- Frontend: `https://gluco-guide.pragnyalabs.com/`
- API root: `https://gluco-guide.pragnyalabs.com/api/`
- API health: `https://gluco-guide.pragnyalabs.com/api/health`
- API check: `https://gluco-guide.pragnyalabs.com/api/auth/check`
