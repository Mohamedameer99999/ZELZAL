"""
ZELZAL v5.0 - Security Modules Package
Each module provides specific cybersecurity functionality for Kali Linux
"""

from .network_protection import NetworkProtection
from .web_protection import WebProtection
from .firewall_advanced import FirewallAdvanced
from .system_protection import SystemProtection
from .performance_protection import PerformanceProtection
from .identity_protection import IdentityProtection
from .container_security import ContainerSecurity
from .wireless_security import WirelessSecurity
from .exploit_detection import ExploitDetection
from .reconnaissance import Reconnaissance
from .web_app_scanning import WebAppScanning
from .exploitation import Exploitation
from .forensics import Forensics

__all__ = [
    "NetworkProtection",
    "WebProtection",
    "FirewallAdvanced",
    "SystemProtection",
    "PerformanceProtection",
    "IdentityProtection",
    "ContainerSecurity",
    "WirelessSecurity",
    "ExploitDetection",
    "Reconnaissance",
    "WebAppScanning",
    "Exploitation",
    "Forensics",
]
