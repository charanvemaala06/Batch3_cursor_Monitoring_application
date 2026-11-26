import pytest

from app.services.server_store import ServerStore, reset_store


@pytest.fixture
def store(tmp_path):
    reset_store()
    path = tmp_path / 'servers.json'
    return ServerStore(storage_path=str(path), secret_key='unit-test-secret')


def test_encrypt_decrypt_roundtrip(store):
    server = {
        'host': '10.0.0.1',
        'name': 'web',
        'os_type': 'linux',
        'port': 22,
        'username': 'ubuntu',
        'password': 's3cret!',
        'sudo_password': '',
    }
    assert store.add_server(server) is True
    listed = store.list_servers()
    assert listed[0]['host'] == '10.0.0.1'
    assert 'password' not in listed[0]

    with_creds = store.get_server('10.0.0.1', with_credentials=True)
    assert with_creds['password'] == 's3cret!'
    without = store.get_server('10.0.0.1', with_credentials=False)
    assert 'password' not in without


def test_duplicate_host_rejected(store):
    server = {
        'host': 'dup.example',
        'name': 'dup',
        'os_type': 'linux',
        'port': 22,
        'username': 'root',
        'password': 'x',
    }
    assert store.add_server(server) is True
    assert store.add_server(server) is False


def test_validate_payload_missing_fields():
    payload, error = ServerStore.validate_payload({'host': 'a'}, require_credentials=True)
    assert payload is None
    assert error


def test_validate_payload_unexpected_fields():
    payload, error = ServerStore.validate_payload({
        'host': 'a.example',
        'username': 'u',
        'password': 'p',
        'evil': True,
    })
    assert payload is None
    assert 'Unexpected' in error


def test_validate_payload_bad_port():
    payload, error = ServerStore.validate_payload({
        'host': 'a.example',
        'username': 'u',
        'password': 'p',
        'port': 99999,
    }, require_credentials=True)
    assert payload is None
    assert 'Port' in error


def test_crud_api(auth_client, app):
    reset_store()
    response = auth_client.post('/api/servers', json={
        'host': '192.168.1.10',
        'name': 'lab',
        'os_type': 'linux',
        'username': 'ops',
        'password': 'hunter2',
        'port': 22,
    })
    assert response.status_code == 201

    listed = auth_client.get('/api/servers?os_type=linux')
    assert listed.status_code == 200
    body = listed.get_json()
    assert len(body) == 1
    assert 'password' not in body[0]

    updated = auth_client.put('/api/servers/192.168.1.10', json={'name': 'lab-2'})
    assert updated.status_code == 200

    deleted = auth_client.delete('/api/servers/192.168.1.10')
    assert deleted.status_code == 200
    assert auth_client.get('/api/servers').get_json() == []


def test_add_server_rejects_unexpected(auth_client):
    response = auth_client.post('/api/servers', json={
        'host': 'x.example',
        'username': 'u',
        'password': 'p',
        'token': 'nope',
    })
    assert response.status_code == 400
