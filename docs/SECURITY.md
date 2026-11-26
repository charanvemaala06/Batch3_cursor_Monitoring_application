# Security notes (local demo)

This app is a **local-only** monitoring demo. Treat it as trusted-LAN / localhost tooling, not a hardened multi-tenant SaaS.

## Secrets

- `SECRET_KEY` must come from the environment; the app fails fast if missing.
- Admin login uses `ADMIN_USERNAME` + `ADMIN_PASSWORD_HASH` (Werkzeug hash). Never commit plain passwords or `.env`.
- Remote SSH passwords in `servers.json` are Fernet-encrypted with a key derived from `SECRET_KEY`. Losing `SECRET_KEY` loses decryptability; rotating it invalidates stored passwords.

## Sessions

- Flask sessions are signed (`SESSION_USE_SIGNER`) and stored on the filesystem for the demo.
- Cookies: `HttpOnly`, `SameSite=Lax`. `Secure` defaults **off** for local HTTP; set `SESSION_COOKIE_SECURE=true` (or use ProductionConfig) behind HTTPS.
- **CSRF:** form POSTs for login rely on same-site cookies. There is no Flask-WTF CSRF token in this demo. Do not expose the app on the public internet without adding CSRF protection and HTTPS.

## APIs & SSH

- Stats and server APIs require a logged-in session; unauthenticated `/api/*` calls return **401**.
- Local metrics use **psutil only** (no shell).
- Remote SSH disables agent/key auto-use; connection timeouts apply; errors returned to the UI are sanitized.
- Remote command output is treated as untrusted and parsed carefully. Prefer not enabling sudo for the demo account.

## Files that must stay out of git

- `.env`
- `app/servers.json` / any `servers.json`
- `flask_session/`, `venv/`, `.venv/`
