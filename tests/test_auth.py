from app.services.auth_service import verify_credentials


def test_login_page_loads(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Username' in response.data


def test_login_success(client):
    response = client.post(
        '/login',
        data={'username': 'admin', 'password': 'testpass'},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/')


def test_login_failure(client):
    response = client.post(
        '/login',
        data={'username': 'admin', 'password': 'wrong'},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data


def test_logout_clears_session(auth_client):
    response = auth_client.get('/logout', follow_redirects=False)
    assert response.status_code == 302
    protected = auth_client.get('/', follow_redirects=False)
    assert protected.status_code == 302
    assert '/login' in protected.headers['Location']


def test_verify_credentials_success(app):
    with app.app_context():
        assert verify_credentials('admin', 'testpass') is True


def test_verify_credentials_failure(app):
    with app.app_context():
        assert verify_credentials('admin', 'nope') is False
        assert verify_credentials('other', 'testpass') is False


def test_verify_credentials_oversized_input(app):
    with app.app_context():
        assert verify_credentials('a' * 200, 'testpass') is False
        assert verify_credentials('admin', 'p' * 600) is False


def test_verify_credentials_missing_config(app, monkeypatch):
    with app.app_context():
        monkeypatch.setitem(app.config, 'ADMIN_USERNAME', None)
        monkeypatch.setitem(app.config, 'ADMIN_PASSWORD_HASH', None)
        assert verify_credentials('admin', 'testpass') is False


def test_dashboard_requires_login(client):
    response = client.get('/', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_api_requires_login_json(client):
    response = client.get('/api/stats')
    assert response.status_code == 401
    assert response.get_json()['error'] == 'Authentication required'
