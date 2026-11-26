# Smoke-test checklist

Run against a local `python run.py` with a filled-in `.env`.

1. [ ] Open `/login` — form renders.
2. [ ] Wrong password → error flash; correct password → dashboard.
3. [ ] Dashboard shows **Local Machine** tile; Linux/Windows tiles open inventory.
4. [ ] Open Local Machine monitor — CPU/memory/disk/process/port panels update (~3s).
5. [ ] Logged-out browser: `GET /api/stats` returns 401.
6. [ ] Add a Linux server (valid host/user/password); list shows it **without** password.
7. [ ] **Test Connection** succeeds against a reachable SSH host (or fails clearly if not).
8. [ ] Monitor remote host — either live metrics or a clear error toast/message.
9. [ ] Delete server — removed from list and dashboard table.
10. [ ] Logout → session cleared; dashboard redirects to login.

Local-only checks (no remote host available): steps 1–5, 6 (add), 9–10 still validate the demo.
