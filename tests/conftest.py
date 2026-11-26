import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.config import TestingConfig
from app.services.server_store import reset_store


@pytest.fixture
def app(tmp_path, monkeypatch):
    password_hash = generate_password_hash('testpass')
    servers_file = tmp_path / 'servers.json'
    monkeypatch.setenv('SECRET_KEY', 'test-secret-key-not-for-production')
    monkeypatch.setenv('ADMIN_USERNAME', 'admin')
    monkeypatch.setenv('ADMIN_PASSWORD_HASH', password_hash)
    monkeypatch.setenv('SERVERS_FILE', str(servers_file))

    class _TestConfig(TestingConfig):
        SECRET_KEY = 'test-secret-key-not-for-production'
        ADMIN_USERNAME = 'admin'
        ADMIN_PASSWORD_HASH = password_hash
        SERVERS_FILE = str(servers_file)

    reset_store()
    application = create_app(_TestConfig)
    application.config['SERVERS_FILE'] = str(servers_file)
    yield application
    reset_store()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(client):
    client.post(
        '/login',
        data={'username': 'admin', 'password': 'testpass'},
        follow_redirects=True,
    )
    return client
