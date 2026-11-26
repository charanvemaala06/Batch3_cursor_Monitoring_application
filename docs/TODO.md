# Monitoring Demo — Implementation TODO

Small, AI-friendly increments for a **local-only** Flask system monitor demo.  
Deploy target: machine where Cursor is running (venv + `python run.py`). No cloud deploy.

---

## 1. Project initialization and Basic UI

- [x] Create project layout (`app/`, `templates/`, `static/`, `run.py`, `.gitignore`)
- [x] Add `requirements.txt` with pinned minimal deps (`flask`, `python-dotenv`)
- [x] Add `.env.example` (no secrets); document copy-to-`.env` in `README.md`
- [x] **Security:** ensure `.env`, `venv/`, `__pycache__/`, session files are in `.gitignore`
- [x] Create Flask app factory (`create_app`) and Dev/Prod config classes
- [x] **Security:** require `SECRET_KEY` from environment; fail fast if missing
- [x] Add base CSS + layout shell (nav, footer, empty main)
- [x] Add Basic UI: home page with a single “Local Machine” tile (static, no live data)
- [x] Document: how to create venv, install deps, set `.env`, run on a local port

---

## 2. Sign-in functionality and unit tests

- [x] Add login page UI (`/login` form: username + password)
- [x] Add logout route that clears the session
- [x] Add `auth_service.verify_credentials` (env-based username + password hash)
- [x] **Security:** store `ADMIN_PASSWORD_HASH` only (Werkzeug hash); never plain passwords in code or git
- [x] **Security:** constant-time username compare; bound password length; use Flask sessions with signer
- [x] Protect dashboard routes with `login_required` redirect to `/login`
- [x] Add unit tests for auth success / failure / missing config / oversized input
- [x] Add `pytest` (+ Flask test client) to `requirements.txt` / `requirements-dev.txt`
- [x] Document: generate password hash command; default local login for demo use only

---

## 3. Local machine monitoring (read-only metrics)

- [x] Add `BaseMonitor` interface (cpu, memory, disk, network, ports, processes)
- [x] Implement local monitor with `psutil` (reuse one implementation for Linux/macOS demo)
- [x] Add `/api/stats` JSON endpoint (auth required)
- [x] **Security:** no shell execution for local stats; auth-only API; no credential leakage in JSON
- [x] Wire monitor page UI + JS poll for local “Local Machine” tile
- [x] Unit tests: mock `psutil`; assert response shape and 401/redirect when logged out
- [x] Document: what metrics are shown; note demo polling interval

---

## 4. Server inventory UI (CRUD shell, no SSH yet)

- [x] Add servers list page (Linux / Windows tabs)
- [x] Add API: list / create / update / delete server metadata (host, name, os, port, username)
- [x] Persist servers to local JSON file (`servers.json`)
- [x] **Security:** encrypt stored passwords with Fernet key derived from `SECRET_KEY`; never return passwords in list API
- [x] **Security:** validate host/os/port; reject unexpected fields
- [x] Unit tests for store encrypt/decrypt and CRUD edge cases (duplicate host, missing fields)
- [x] Document: where `servers.json` lives; that it must not be committed

---

## 5. Remote monitoring over SSH

- [x] Add connection test endpoint (`/api/servers/test`) using Paramiko
- [x] Implement `RemoteMonitor` for Linux (SSH + safe read-only commands)
- [x] Implement minimal Windows remote stats (SSH + PowerShell read-only)
- [x] Add `/api/stats/<host>` for remote hosts (auth required)
- [x] **Security:** disable SSH agent/key auto-use in demo connect; timeouts; no sudo by default; sanitize errors returned to UI
- [x] **Security:** treat remote output as untrusted; parse carefully; avoid injecting host/user into shell strings unsafely
- [x] Hook monitor page to remote host; show errors clearly on failure
- [x] Unit tests: mock Paramiko; success + auth failure + timeout paths
- [x] Document: SSH prerequisites for local demo (reachable host, credentials)

---

## 6. Dashboard polish and UX hardening

- [x] Finalize dashboard tiles (Local Machine, Linux servers, Windows servers)
- [x] Empty states, loading states, and basic error toasts
- [x] **Security:** CSRF strategy for cookie session (same-site cookies / Flask-WTF or documented demo limitation)
- [x] **Security:** set secure session cookie flags appropriate for local HTTP demo (document prod vs local)
- [x] Smoke-test checklist in `docs/` (login → local stats → add server → test → monitor)
- [x] Update `README.md` with screenshots or short UI walkthrough

---

## 7. CI/CD (GitHub Actions) — local-quality gates

- [x] Add `.github/workflows/ci.yml`
- [x] Job: install deps from lock/requirements on Ubuntu
- [x] Job: run unit tests with pytest
- [x] Job: lint (ruff or flake8) — fail on high-severity issues only if configured
- [x] **Security:** CI must not use real secrets; inject dummy `SECRET_KEY` / test admin hash via env
- [x] **Security:** dependency audit step optional (`pip-audit`) — non-blocking or blocking as agreed
- [x] Document: what CI checks; how to run the same checks locally before push

---

## 8. Docs and local run freeze

- [x] `README.md`: one-page local run (venv, `.env`, port, login)
- [x] `docs/SECURITY.md`: threat notes for a local demo (secrets, SSH, encrypted store, session)
- [x] `docs/ARCHITECTURE.md`: routes, services, data flow (short)
- [x] Confirm `.env.example` matches all required vars
- [x] Final pass: every feature above has a checkbox owner note in this file if deferred

---

## Suggested AI increment size

Do **one checkbox group (or one checkbox)** per agent turn when possible:  
implement → add/adjust tests → update the matching doc line → mark the box done.
