from unittest.mock import MagicMock, patch

import paramiko

from app.services.remote_monitor import RemoteMonitor, sanitize_remote_error


def test_sanitize_auth_error():
    assert sanitize_remote_error(paramiko.AuthenticationException()) == 'Authentication failed'


def test_sanitize_strips_password_fragments():
    message = sanitize_remote_error(Exception('failed password=supersecret host=x'))
    assert 'supersecret' not in message
    assert 'password=***' in message


@patch('app.services.remote_monitor.paramiko.SSHClient')
def test_connection_success(mock_client_cls):
    client = MagicMock()
    mock_client_cls.return_value = client
    monitor = RemoteMonitor('1.2.3.4', 'user', 'pass', port=22, os_type='linux')
    ok, message = monitor.test_connection()
    assert ok is True
    assert 'successful' in message.lower()
    client.connect.assert_called_once()
    kwargs = client.connect.call_args.kwargs
    assert kwargs['allow_agent'] is False
    assert kwargs['look_for_keys'] is False


@patch('app.services.remote_monitor.paramiko.SSHClient')
def test_connection_auth_failure(mock_client_cls):
    client = MagicMock()
    mock_client_cls.return_value = client
    client.connect.side_effect = paramiko.AuthenticationException('bad')
    monitor = RemoteMonitor('1.2.3.4', 'user', 'pass')
    ok, message = monitor.test_connection()
    assert ok is False
    assert 'Authentication failed' in message


@patch('app.services.remote_monitor.paramiko.SSHClient')
def test_connection_timeout(mock_client_cls):
    client = MagicMock()
    mock_client_cls.return_value = client
    client.connect.side_effect = TimeoutError('timed out')
    monitor = RemoteMonitor('1.2.3.4', 'user', 'pass')
    ok, message = monitor.test_connection()
    assert ok is False
    assert 'timed out' in message.lower()


@patch('app.routes.servers.RemoteMonitor')
def test_test_endpoint(mock_remote, auth_client):
    instance = MagicMock()
    instance.test_connection.return_value = (True, 'Connection successful')
    mock_remote.return_value = instance
    response = auth_client.post('/api/servers/test', json={
        'host': '10.0.0.5',
        'username': 'ops',
        'password': 'x',
        'port': 22,
        'os_type': 'linux',
    })
    assert response.status_code == 200
    assert response.get_json()['success'] is True
