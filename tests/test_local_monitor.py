from unittest.mock import MagicMock, patch

from app.services.local_monitor import LocalMonitor


def _fake_cpu_freq():
    freq = MagicMock()
    freq.current = 2400.0
    freq.min = 800.0
    freq.max = 3200.0
    return freq


def _fake_memory():
    mem = MagicMock()
    mem.total = 8_000_000_000
    mem.available = 4_000_000_000
    mem.used = 4_000_000_000
    mem.percent = 50.0
    return mem


def _fake_swap():
    swap = MagicMock()
    swap.total = 1_000_000_000
    swap.used = 100_000_000
    swap.percent = 10.0
    return swap


@patch('app.services.local_monitor.psutil')
def test_get_all_stats_shape(mock_psutil):
    mock_psutil.cpu_percent.return_value = 12.5
    mock_psutil.cpu_count.return_value = 4
    mock_psutil.cpu_freq.return_value = _fake_cpu_freq()
    mock_psutil.virtual_memory.return_value = _fake_memory()
    mock_psutil.swap_memory.return_value = _fake_swap()
    mock_psutil.disk_partitions.return_value = []
    mock_psutil.net_io_counters.return_value = MagicMock(
        bytes_sent=100, bytes_recv=200, packets_sent=1, packets_recv=2
    )
    mock_psutil.net_if_addrs.return_value = {}
    mock_psutil.net_connections.return_value = []
    mock_psutil.process_iter.return_value = []

    stats = LocalMonitor().get_all_stats()
    assert set(stats.keys()) == {
        'cpu', 'memory', 'disk', 'network', 'ports', 'processes',
    }
    assert stats['cpu']['percent'] == 12.5
    assert stats['cpu']['count'] == 4
    assert stats['memory']['percent'] == 50.0
    assert stats['network']['bytes_sent'] == 100
    assert stats['disk'] == []
    assert stats['ports'] == []
    assert stats['processes'] == []


def test_api_stats_requires_auth(client):
    response = client.get('/api/stats')
    assert response.status_code == 401


@patch('app.routes.dashboard.get_monitor')
def test_api_stats_authenticated(mock_get_monitor, auth_client):
    monitor = MagicMock()
    monitor.get_all_stats.return_value = {
        'cpu': {'percent': 1, 'count': 2, 'frequency': {'current': 1000}},
        'memory': {'percent': 10, 'total': 1, 'used': 1, 'available': 0},
        'disk': [],
        'network': {'bytes_sent': 0, 'bytes_recv': 0},
        'ports': [],
        'processes': [],
    }
    mock_get_monitor.return_value = monitor

    response = auth_client.get('/api/stats')
    assert response.status_code == 200
    body = response.get_json()
    assert body['cpu']['percent'] == 1
    assert 'password' not in body
