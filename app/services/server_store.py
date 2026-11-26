"""Encrypted persistence for remote server metadata."""
import base64
import hashlib
import json
import os
import re
from typing import Any

from cryptography.fernet import Fernet


HOST_RE = re.compile(r'^[A-Za-z0-9._:-]{1,253}$')
USERNAME_RE = re.compile(r'^[A-Za-z0-9._@\\-]{1,128}$')
VALID_OS = frozenset({'linux', 'windows'})
ALLOWED_FIELDS = frozenset({
    'host', 'name', 'os_type', 'port', 'username', 'password', 'sudo_password',
})


class ServerStore:
    """Persists monitored server configs in a local JSON file.

    Passwords are encrypted with a Fernet key derived from SECRET_KEY.
    List/get without credentials never return passwords.
    """

    def __init__(self, storage_path: str | None = None, secret_key: str | None = None):
        self.storage_path = storage_path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'servers.json',
        )
        secret = secret_key or os.getenv('SECRET_KEY')
        if not secret:
            raise RuntimeError('SECRET_KEY must be set in the environment (via .env).')
        digest = hashlib.sha256(secret.encode()).digest()
        self._fernet = Fernet(base64.urlsafe_b64encode(digest))
        directory = os.path.dirname(self.storage_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        if not os.path.exists(self.storage_path):
            self._save({})

    def _encrypt(self, value: str | None) -> str | None:
        if not value:
            return None
        return self._fernet.encrypt(value.encode()).decode()

    def _decrypt(self, value: str | None) -> str | None:
        if not value:
            return None
        try:
            return self._fernet.decrypt(value.encode()).decode()
        except Exception:
            return None

    def _load(self) -> dict:
        with open(self.storage_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save(self, data: dict) -> None:
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def validate_payload(data: dict[str, Any], *, require_credentials: bool = False) -> tuple[dict | None, str | None]:
        """Validate and normalize server fields. Rejects unexpected keys."""
        if not isinstance(data, dict):
            return None, 'Invalid payload'
        unexpected = set(data.keys()) - ALLOWED_FIELDS
        if unexpected:
            return None, f'Unexpected fields: {", ".join(sorted(unexpected))}'

        host = (data.get('host') or '').strip()
        username = (data.get('username') or '').strip()
        os_type = (data.get('os_type') or 'linux').strip().lower()
        name = (data.get('name') or host).strip()
        password = data.get('password') or ''
        sudo_password = data.get('sudo_password') or ''

        try:
            port = int(data.get('port') or 22)
        except (TypeError, ValueError):
            return None, 'Port must be an integer'

        if not host or not HOST_RE.match(host):
            return None, 'Invalid host'
        if not username or not USERNAME_RE.match(username):
            return None, 'Invalid username'
        if os_type not in VALID_OS:
            return None, 'Invalid OS type'
        if port < 1 or port > 65535:
            return None, 'Port out of range'
        if require_credentials and not password:
            return None, 'Password is required'
        if len(password) > 512 or len(sudo_password) > 512:
            return None, 'Password too long'
        if len(name) > 128:
            return None, 'Name too long'

        return {
            'host': host,
            'name': name,
            'os_type': os_type,
            'port': port,
            'username': username,
            'password': password,
            'sudo_password': sudo_password,
        }, None

    def add_server(self, server: dict) -> bool:
        data = self._load()
        host = server['host']
        if host in data:
            return False
        stored = {
            'host': host,
            'name': server.get('name') or host,
            'os_type': server['os_type'],
            'port': server['port'],
            'username': server['username'],
            'password': self._encrypt(server.get('password')),
            'sudo_password': self._encrypt(server.get('sudo_password')),
        }
        data[host] = stored
        self._save(data)
        return True

    def update_server(self, host: str, updates: dict) -> bool:
        data = self._load()
        if host not in data:
            return False
        current = data[host]
        if 'password' in updates and updates.get('password'):
            current['password'] = self._encrypt(updates['password'])
        if 'sudo_password' in updates and updates.get('sudo_password'):
            current['sudo_password'] = self._encrypt(updates['sudo_password'])
        for key in ('name', 'port', 'username', 'os_type'):
            if key in updates and updates[key] is not None:
                current[key] = updates[key]
        data[host] = current
        self._save(data)
        return True

    def remove_server(self, host: str) -> bool:
        data = self._load()
        if host not in data:
            return False
        del data[host]
        self._save(data)
        return True

    def get_server(self, host: str, with_credentials: bool = False) -> dict | None:
        data = self._load()
        server = data.get(host)
        if not server:
            return None
        server = dict(server)
        server['host'] = host
        if with_credentials:
            server['password'] = self._decrypt(server.get('password'))
            server['sudo_password'] = self._decrypt(server.get('sudo_password'))
        else:
            server.pop('password', None)
            server.pop('sudo_password', None)
        return server

    def list_servers(self, os_type: str | None = None) -> list[dict]:
        data = self._load()
        servers = []
        for host, server in data.items():
            item = dict(server)
            item['host'] = host
            item.pop('password', None)
            item.pop('sudo_password', None)
            if os_type and item.get('os_type') != os_type:
                continue
            servers.append(item)
        return servers


_store: ServerStore | None = None


def get_store(storage_path: str | None = None, secret_key: str | None = None) -> ServerStore:
    """Return the process-wide store, creating it on first use."""
    global _store
    if storage_path is not None or secret_key is not None:
        return ServerStore(storage_path=storage_path, secret_key=secret_key)
    if _store is None:
        from flask import current_app

        path = current_app.config.get('SERVERS_FILE')
        secret = current_app.config.get('SECRET_KEY')
        _store = ServerStore(storage_path=path, secret_key=secret)
    return _store


def reset_store() -> None:
    """Clear the cached store (for tests)."""
    global _store
    _store = None
