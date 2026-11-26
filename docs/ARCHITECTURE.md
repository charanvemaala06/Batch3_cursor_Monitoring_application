# Architecture

Short map of the local Flask monitor.

## Layout

```
app/
  app.py              # create_app factory
  config.py           # Dev / Prod / Testing
  routes/             # Blueprints: auth, dashboard, servers
  services/           # auth, local/remote monitors, server_store
  templates/ static/  # UI
run.py                # Local entry: python run.py
```

## Request flow

1. **Login** (`auth` blueprint) → `auth_service.verify_credentials` → Flask session.
2. **Dashboard** (`/`) lists Local Machine tile + Linux/Windows inventory counts.
3. **Local stats** → `GET /api/stats` → `LocalMonitor` (psutil) → JSON.
4. **Server CRUD** → `/api/servers` → `ServerStore` (encrypted JSON file).
5. **Remote stats** → `GET /api/stats/<host>` → decrypt creds → `RemoteMonitor` (Paramiko) → JSON.
6. **Monitor UI** polls every ~3s via `static/js/dashboard.js`.

## Key types

| Piece | Role |
|-------|------|
| `BaseMonitor` | Interface: cpu, memory, disk, network, ports, processes |
| `LocalMonitor` | One implementation for the host running Flask |
| `RemoteMonitor` | Linux SSH command set + minimal Windows PowerShell |
| `ServerStore` | Validate → encrypt passwords → `servers.json` |

## Auth

`login_required` redirects HTML to `/login` and returns JSON 401 for `/api/*`.
