# Monitoring Demo

Local-only Flask system monitor: sign in, view this machine’s metrics, and manage remote Linux/Windows hosts over SSH.

## Quick start

```bash
cd monitoring_demo
python3 -m venv .venv
source .venv/bin/activate
pip install -r app/requirements.txt

cp .env.example .env
# Edit .env — set SECRET_KEY, ADMIN_USERNAME, ADMIN_PASSWORD_HASH

python run.py
# Open http://127.0.0.1:5000  (or set PORT=5080 in .env if 5000 is busy)
```


### Generate secrets

```bash
python -c "import secrets; print(secrets.token_hex(32))"
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your-password'))"
```

Demo login is whatever you put in `.env` (`ADMIN_USERNAME` + password matching `ADMIN_PASSWORD_HASH`). For local demos only — do not reuse production credentials.

## What you get

| Area | Notes |
|------|--------|
| Local metrics | CPU, memory, disk, network, listening ports, top processes via `psutil` (no shell) |
| Polling | Monitor UI refreshes about every **3 seconds** |
| Servers | CRUD for host metadata in `app/servers.json` (gitignored); passwords Fernet-encrypted from `SECRET_KEY` |
| Remote | SSH via Paramiko (`allow_agent=False`, `look_for_keys=False`); Linux full stats, Windows minimal |

## Dev checks (same as CI)

```bash
pip install -r requirements-dev.txt
pytest
ruff check app tests
```

## Docs

- [Architecture](docs/ARCHITECTURE.md)
- [Security notes](docs/SECURITY.md)
- [Smoke-test checklist](docs/SMOKE_TEST.md)
- [Implementation TODO](docs/TODO.md)
