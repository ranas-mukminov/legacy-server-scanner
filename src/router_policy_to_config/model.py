"""
Data models for router policy configuration.

These models provide a vendor-agnostic representation of network policies.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any


class VendorType(str, Enum):
    """Supported router vendors."""
    ROUTEROS = "routeros"
    OPENWRT = "openwrt"


class WANType(str, Enum):
    """WAN connection types."""
    PPPOE = "pppoe"
    DHCP = "dhcp"
    STATIC = "static"


class WiFiMode(str, Enum):
    """Wi-Fi operating modes."""
    AP = "ap"
    STATION = "station"


class WiFiEncryption(str, Enum):
    """Wi-Fi encryption types."""
    OPEN = "open"
    WEP = "wep"
    WPA_PSK = "wpa-psk"
    WPA2_PSK = "wpa2-psk"
    WPA3_SAE = "wpa3-sae"
    WPA2_ENTERPRISE = "wpa2-enterprise"


class VPNType(str, Enum):
    """VPN types."""
    WIREGUARD = "wireguard"
    OPENVPN = "openvpn"
    L2TP = "l2tp"
    IPSEC = "ipsec"
    PPTP = "pptp"


class VPNRole(str, Enum):
    """VPN role."""
    SERVER = "server"
    CLIENT = "client"


class FirewallAction(str, Enum):
    """Firewall rule actions."""
    ACCEPT = "accept"
    DROP = "drop"
    REJECT = "reject"


class Protocol(str, Enum):
    """Network protocols."""
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    ALL = "all"


@dataclass
class VendorTarget:
    """Target vendor configuration."""
    vendor: VendorType
    version: Optional[str] = None


@dataclass
class Meta:
    """Policy metadata."""
    name: str
    description: Optional[str] = None
    target: Optional[VendorTarget] = None


@dataclass
class WAN:
    """WAN configuration."""
    type: WANType
    interface: str
    username: Optional[str] = None
    password_ref: Optional[str] = None
    ip_address: Optional[str] = None
    netmask: Optional[str] = None
    gateway: Optional[str] = None
    dns: List[str] = field(default_factory=list)
    mtu: Optional[int] = None


@dataclass
class DHCPConfig:
    """DHCP server configuration."""
    enabled: bool = False
    range: Optional[str] = None
    lease_time: Optional[str] = None
    dns: List[str] = field(default_factory=list)


@dataclass
class LAN:
    """LAN network configuration."""
    name: str
    subnet: str
    gateway: str
    vlan_id: Optional[int] = None
    dhcp: Optional[DHCPConfig] = None
    isolated_from: List[str] = field(default_factory=list)


@dataclass
class WiFiSecurity:
    """Wi-Fi security configuration."""
    encryption: WiFiEncryption
    password_ref: Optional[str] = None


@dataclass
class WiFi:
    """Wi-Fi network configuration."""
    name: str
    lan: str
    ssid: str
    mode: WiFiMode
    security: WiFiSecurity
    band: Optional[str] = None
    channel: Optional[int] = None
    guest: bool = False
    hidden: bool = False


@dataclass
class VPN:
    """VPN configuration."""
    type: VPNType
    role: VPNRole
    listen_port: Optional[int] = None
    remote_host: Optional[str] = None
    remote_port: Optional[int] = None
    allowed_ips: List[str] = field(default_factory=list)
    public_key_ref: Optional[str] = None
    private_key_ref: Optional[str] = None
    preshared_key_ref: Optional[str] = None


@dataclass
class FirewallRule:
    """Firewall rule."""
    name: str
    action: FirewallAction
    from_zones: List[str] = field(default_factory=list)
    to_zones: List[str] = field(default_factory=list)
    protocol: Optional[Protocol] = None
    port: Optional[str] = None
    comment: Optional[str] = None


@dataclass
class Firewall:
    """Firewall configuration."""
    default_policy: FirewallAction = FirewallAction.DROP
    rules: List[FirewallRule] = field(default_factory=list)


@dataclass
class PortForward:
    """Port forwarding rule."""
    name: str
    external_port: int
    internal_ip: str
    internal_port: int
    protocol: str = "tcp"


@dataclass
class NAT:
    """NAT configuration."""
    masquerade: bool = True
    port_forwards: List[PortForward] = field(default_factory=list)


@dataclass
class DNSRecord:
    """Static DNS record."""
    name: str
    ip: str


@dataclass
class DNS:
    """DNS configuration."""
    forwarders: List[str] = field(default_factory=list)
    local_domain: Optional[str] = None
    static_records: List[DNSRecord] = field(default_factory=list)


@dataclass
class Policy:
    """Complete router policy."""
    meta: Meta
    wan: WAN
    lans: List[LAN] = field(default_factory=list)
    wifi: List[WiFi] = field(default_factory=list)
    vpn: List[VPN] = field(default_factory=list)
    firewall: Optional[Firewall] = None
    nat: Optional[NAT] = None
    dns: Optional[DNS] = None

    def get_lan_by_name(self, name: str) -> Optional[LAN]:
        """Get LAN configuration by name."""
        for lan in self.lans:
            if lan.name == name:
                return lan
        return None

    def get_wifi_by_lan(self, lan_name: str) -> List[WiFi]:
        """Get all Wi-Fi networks for a given LAN."""
        return [w for w in self.wifi if w.lan == lan_name]
