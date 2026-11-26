from flask import Blueprint, jsonify, redirect, render_template, url_for

from app.routes.decorators import login_required
from app.services import get_monitor
from app.services.remote_monitor import RemoteMonitor, sanitize_remote_error
from app.services.server_store import get_store

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    store = get_store()
    servers = store.list_servers()
    linux_servers = [s for s in servers if s.get('os_type') == 'linux']
    windows_servers = [s for s in servers if s.get('os_type') == 'windows']
    return render_template(
        'index.html',
        linux_servers=linux_servers,
        windows_servers=windows_servers,
    )


@dashboard_bp.route('/monitor/<path:host>')
@login_required
def monitor(host):
    if host == 'localhost':
        return render_template('monitor.html', host='localhost', system_type='local')
    store = get_store()
    server = store.get_server(host)
    if not server:
        return redirect(url_for('dashboard.index'))
    return render_template(
        'monitor.html',
        host=host,
        system_type=server.get('os_type'),
    )


@dashboard_bp.route('/api/stats')
@login_required
def get_stats():
    monitor = get_monitor()
    return jsonify(monitor.get_all_stats())


@dashboard_bp.route('/api/stats/<path:host>')
@login_required
def get_remote_stats(host):
    if host == 'localhost':
        monitor = get_monitor()
        return jsonify(monitor.get_all_stats())

    store = get_store()
    server = store.get_server(host, with_credentials=True)
    if not server:
        return jsonify({'error': 'Server not found'}), 404
    try:
        remote = RemoteMonitor(
            host=server['host'],
            username=server['username'],
            password=server['password'] or '',
            port=int(server['port'] or 22),
            os_type=server['os_type'],
        )
        return jsonify(remote.get_all_stats())
    except Exception as exc:
        return jsonify({'error': sanitize_remote_error(exc)}), 502
