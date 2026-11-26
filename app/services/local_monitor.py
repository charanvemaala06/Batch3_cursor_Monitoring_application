"""Local machine metrics via psutil (no shell execution)."""
import psutil

from .base_monitor import BaseMonitor


class LocalMonitor(BaseMonitor):
    """Read-only local system stats using psutil only."""

    def get_cpu_usage(self):
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()

        return {
            'percent': cpu_percent,
            'count': cpu_count,
            'frequency': {
                'current': cpu_freq.current if cpu_freq else 0,
                'min': cpu_freq.min if cpu_freq else 0,
                'max': cpu_freq.max if cpu_freq else 0,
            },
        }

    def get_memory_usage(self):
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()

        return {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'percent': memory.percent,
            'swap_total': swap.total,
            'swap_used': swap.used,
            'swap_percent': swap.percent,
        }

    def get_disk_usage(self):
        partitions = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                partitions.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent,
                })
            except (PermissionError, OSError):
                continue
        return partitions

    def get_network_usage(self):
        net_io = psutil.net_io_counters()
        interfaces = {}

        for iface, addrs in psutil.net_if_addrs().items():
            addresses = []
            for addr in addrs:
                family = getattr(addr.family, 'name', str(addr.family))
                if family in ('AF_INET', '2'):
                    addresses.append({
                        'address': addr.address,
                        'netmask': addr.netmask,
                    })
            if addresses:
                interfaces[iface] = addresses

        return {
            'bytes_sent': net_io.bytes_sent if net_io else 0,
            'bytes_recv': net_io.bytes_recv if net_io else 0,
            'packets_sent': net_io.packets_sent if net_io else 0,
            'packets_recv': net_io.packets_recv if net_io else 0,
            'interfaces': interfaces,
        }

    def get_open_ports(self):
        ports = []
        try:
            connections = psutil.net_connections(kind='inet')
        except (psutil.AccessDenied, PermissionError):
            return ports

        for conn in connections:
            if conn.status != 'LISTEN':
                continue
            family = getattr(conn.family, 'name', str(conn.family))
            sock_type = getattr(conn.type, 'name', str(conn.type))
            ports.append({
                'fd': conn.fd,
                'family': family,
                'type': sock_type,
                'local_address': (
                    f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None
                ),
                'remote_address': (
                    f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None
                ),
                'status': conn.status,
                'pid': conn.pid,
            })
        return sorted(ports, key=lambda x: x.get('local_address') or '')

    def get_top_processes(self, limit=10):
        processes = []
        for proc in psutil.process_iter(
            ['pid', 'name', 'cpu_percent', 'memory_percent', 'status']
        ):
            try:
                pinfo = proc.info
                if pinfo['cpu_percent'] is None or pinfo['memory_percent'] is None:
                    continue
                processes.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'],
                    'cpu_percent': pinfo['cpu_percent'],
                    'memory_percent': round(pinfo['memory_percent'], 2),
                    'status': pinfo['status'],
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        return processes[:limit]
