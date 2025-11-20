"""
router-policy-to-config: AI-assisted copilot for router configuration

This package provides tools to convert high-level YAML network policies
into vendor-specific router configurations (RouterOS, OpenWrt).
"""

__version__ = "0.1.0"
__author__ = "run-as-daemon"
__email__ = "support@run-as-daemon.ru"
__url__ = "https://run-as-daemon.ru"

from .model import Policy, WAN, LAN, WiFi, VPN, Firewall

__all__ = [
    "Policy",
    "WAN",
    "LAN",
    "WiFi",
    "VPN",
    "Firewall",
]
