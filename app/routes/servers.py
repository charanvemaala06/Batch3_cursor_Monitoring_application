from flask import Blueprint, jsonify, render_template, request

from app.routes.decorators import login_required
from app.services.remote_monitor import RemoteMonitor, sanitize_remote_error
from app.services.server_store import VALID_OS, ServerStore, get_store

servers_bp = Blueprint('servers', __name__)


@servers_bp.route('/servers')
@login_required
def index():
    os_type = request.args.get('os_type', 'linux')
    if os_type not in VALID_OS:
        os_type = 'linux'
    servers = get_store().list_servers(os_type=os_type)
    return render_template('servers.html', os_type=os_type, servers=servers)


@servers_bp.route('/api/servers')
@login_required
def list_servers():
    os_type = request.args.get('os_type')
    if os_type and os_type not in VALID_OS:
        return jsonify({'error': 'Invalid OS type'}), 400
    return jsonify(get_store().list_servers(os_type=os_type))


@servers_bp.route('/api/servers', methods=['POST'])
@login_required
def add_server():
    data = request.get_json(silent=True) or {}
    server, error = ServerStore.validate_payload(data, require_credentials=True)
    if error:
        return jsonify({'error': error}), 400
    if not get_store().add_server(server):
        return jsonify({'error': f"Server {server['host']} already exists"}), 409
    return jsonify({'success': True, 'host': server['host']}), 201


@servers_bp.route('/api/servers/<host>', methods=['PUT'])
@login_required
def update_server(host):
    data = request.get_json(silent=True) or {}
    allowed = {'name', 'port', 'password', 'username', 'os_type', 'sudo_password'}
    unexpected = set(data.keys()) - allowed
    if unexpected:
        return jsonify({'error': f'Unexpected fields: {", ".join(sorted(unexpected))}'}), 400

    updates = {}
    if 'port' in data:
        try:
            port = int(data['port'])
        except (TypeError, ValueError):
            return jsonify({'error': 'Port must be an integer'}), 400
        if port < 1 or port > 65535:
            return jsonify({'error': 'Port out of range'}), 400
        updates['port'] = port
    if 'password' in data and data['password']:
        if len(str(data['password'])) > 512:
            return jsonify({'error': 'Password too long'}), 400
        updates['password'] = data['password']
    if 'name' in data:
        updates['name'] = (data['name'] or host).strip()[:128]
    if 'username' in data and data['username']:
        updates['username'] = str(data['username']).strip()
    if 'os_type' in data:
        os_type = str(data['os_type']).lower()
        if os_type not in VALID_OS:
            return jsonify({'error': 'Invalid OS type'}), 400
        updates['os_type'] = os_type

    if not get_store().update_server(host, updates):
        return jsonify({'error': 'Server not found'}), 404
    return jsonify({'success': True})


@servers_bp.route('/api/servers/<host>', methods=['DELETE'])
@login_required
def delete_server(host):
    if not get_store().remove_server(host):
        return jsonify({'error': 'Server not found'}), 404
    return jsonify({'success': True})


@servers_bp.route('/api/servers/test', methods=['POST'])
@login_required
def test_connection():
    data = request.get_json(silent=True) or {}
    payload, error = ServerStore.validate_payload(data, require_credentials=True)
    if error:
        return jsonify({'success': False, 'message': error}), 400
    try:
        monitor = RemoteMonitor(
            host=payload['host'],
            username=payload['username'],
            password=payload['password'],
            port=payload['port'],
            os_type=payload['os_type'],
        )
        ok, message = monitor.test_connection()
        return jsonify({'success': ok, 'message': message})
    except Exception as exc:
        return jsonify({'success': False, 'message': sanitize_remote_error(exc)}), 502


@servers_bp.route('/api/servers/<host>/stats')
@login_required
def server_stats(host):
    server = get_store().get_server(host, with_credentials=True)
    if not server:
        return jsonify({'error': 'Server not found'}), 404
    try:
        monitor = RemoteMonitor(
            host=server['host'],
            username=server['username'],
            password=server['password'] or '',
            port=int(server['port'] or 22),
            os_type=server['os_type'],
        )
        return jsonify(monitor.get_all_stats())
    except Exception as exc:
        return jsonify({'error': sanitize_remote_error(exc)}), 502
