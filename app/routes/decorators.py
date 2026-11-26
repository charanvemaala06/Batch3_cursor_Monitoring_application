"""Shared route decorators."""
from functools import wraps

from flask import jsonify, redirect, request, session, url_for


def login_required(f):
    """Require a logged-in session.

    HTML routes redirect to /login; API routes under /api/ return 401 JSON.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('logged_in'):
            return f(*args, **kwargs)
        if request.path.startswith('/api/') or request.accept_mimetypes.best == 'application/json':
            return jsonify({'error': 'Authentication required'}), 401
        return redirect(url_for('auth.login'))

    return decorated_function
