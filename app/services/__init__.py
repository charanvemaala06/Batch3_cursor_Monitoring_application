"""Monitor factory — one local implementation covers Linux/macOS demo hosts."""
from .base_monitor import BaseMonitor
from .local_monitor import LocalMonitor


def get_monitor() -> BaseMonitor:
    return LocalMonitor()
