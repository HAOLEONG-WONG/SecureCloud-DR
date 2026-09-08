# Application — SecureCloud-DR Lab Web App

## What
A minimal Flask + Nginx + Gunicorn web application with a login form, 
backed by SQLite, deployed on the lab VM (`vm-web-01`).

## Why
Exists to generate realistic authentication telemetry for later detection 
engineering (Phase 6) and attack simulation (Phase 7) — not intended to be 
a polished product.

## How
- `app.py` — Flask app with `/` and `/login` routes
- `setup_db.py` — initializes SQLite `users.db` with one test user
- `check_db.py` — quick utility to inspect database contents
- Served via Gunicorn (127.0.0.1:5000), reverse-proxied by Nginx (port 80)
- Runs as a systemd service (`webapp.service`) on the VM

## Intentional Vulnerability
The `/login` route builds its SQL query via f-string concatenation rather 
than parameterized queries — a deliberate weakness for Phase 7 SQL 
Injection simulation. See `docs/03-architecture.md` for the corrected/secure 
version reference.

## Local Setup (to redeploy on a fresh VM)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 setup_db.py
gunicorn --bind 127.0.0.1:5000 app:app
```

## Logging
Authentication events are logged as structured JSON to `auth.log` 
(not committed — runtime artifact, may contain real IPs).