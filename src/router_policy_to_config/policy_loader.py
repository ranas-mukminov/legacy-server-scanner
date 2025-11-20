"""
Policy loader and validator.

Loads YAML policy files and validates them against the schema.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import yaml

from .model import (
    Policy, Meta, VendorTarget, WAN, LAN, WiFi, VPN, Firewall,
    NAT, DNS, DHCPConfig, WiFiSecurity, FirewallRule, PortForward, DNSRecord,
    VendorType, WANType, WiFiMode, WiFiEncryption, VPNType, VPNRole,
    FirewallAction, Protocol
)


class PolicyLoadError(Exception):
    """Exception raised when policy loading fails."""
    pass


class SecretResolver:
    """Resolves secret references from environment variables."""
    
    def __init__(self, prefix: str = "ROUTER_SECRET_"):
        self.prefix = prefix
    
    def resolve(self, ref: str) -> Optional[str]:
        """
        Resolve a secret reference like 'secret:pppoe_password' to actual value.
        
        Looks for environment variable ROUTER_SECRET_PPPOE_PASSWORD.
        """
        if not ref or not ref.startswith("secret:"):
            return ref
        
        secret_name = ref.replace("secret:", "").upper()
        env_var = f"{self.prefix}{secret_name}"
        return os.getenv(env_var)


def load_policy_yaml(path: Path, resolve_secrets: bool = False) -> Policy:
    """
    Load and parse a policy YAML file.
    
    Args:
        path: Path to YAML file
        resolve_secrets: Whether to resolve secret references from environment
        
    Returns:
        Policy object
        
    Raises:
        PolicyLoadError: If policy cannot be loaded or parsed
    """
    if not path.exists():
        raise PolicyLoadError(f"Policy file not found: {path}")
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise PolicyLoadError(f"Invalid YAML: {e}")
    
    if not data:
        raise PolicyLoadError("Empty policy file")
    
    secret_resolver = SecretResolver() if resolve_secrets else None
    
    try:
        return _parse_policy(data, secret_resolver)
    except (KeyError, ValueError, TypeError) as e:
        raise PolicyLoadError(f"Invalid policy structure: {e}")


def _parse_policy(data: Dict[str, Any], secret_resolver: Optional[SecretResolver]) -> Policy:
    """Parse policy data into Policy object."""
    
    # Parse meta
    meta_data = data.get('meta', {})
    target_data = meta_data.get('target', {})
    vendor_target = VendorTarget(
        vendor=VendorType(target_data.get('vendor', 'routeros')),
        version=target_data.get('version')
    ) if target_data else None
    
    meta = Meta(
        name=meta_data['name'],
        description=meta_data.get('description'),
        target=vendor_target
    )
    
    # Parse WAN
    wan_data = data.get('wan', {})
    wan = WAN(
        type=WANType(wan_data['type']),
        interface=wan_data['interface'],
        username=wan_data.get('username'),
        password_ref=_resolve_secret(wan_data.get('password_ref'), secret_resolver),
        ip_address=wan_data.get('ip_address'),
        netmask=wan_data.get('netmask'),
        gateway=wan_data.get('gateway'),
        dns=wan_data.get('dns', []),
        mtu=wan_data.get('mtu')
    )
    
    # Parse LANs
    lans = []
    for lan_data in data.get('lans', []):
        dhcp_data = lan_data.get('dhcp')
        dhcp = None
        if dhcp_data:
            dhcp = DHCPConfig(
                enabled=dhcp_data.get('enabled', False),
                range=dhcp_data.get('range'),
                lease_time=dhcp_data.get('lease_time'),
                dns=dhcp_data.get('dns', [])
            )
        
        lan = LAN(
            name=lan_data['name'],
            subnet=lan_data['subnet'],
            gateway=lan_data['gateway'],
            vlan_id=lan_data.get('vlan_id'),
            dhcp=dhcp,
            isolated_from=lan_data.get('isolated_from', [])
        )
        lans.append(lan)
    
    # Parse Wi-Fi
    wifi_list = []
    for wifi_data in data.get('wifi', []):
        security_data = wifi_data.get('security', {})
        security = WiFiSecurity(
            encryption=WiFiEncryption(security_data.get('encryption', 'wpa2-psk')),
            password_ref=_resolve_secret(security_data.get('password_ref'), secret_resolver)
        )
        
        wifi = WiFi(
            name=wifi_data['name'],
            lan=wifi_data['lan'],
            ssid=wifi_data['ssid'],
            mode=WiFiMode(wifi_data['mode']),
            security=security,
            band=wifi_data.get('band'),
            channel=wifi_data.get('channel'),
            guest=wifi_data.get('guest', False),
            hidden=wifi_data.get('hidden', False)
        )
        wifi_list.append(wifi)
    
    # Parse VPN
    vpn_list = []
    for vpn_data in data.get('vpn', []):
        vpn = VPN(
            type=VPNType(vpn_data['type']),
            role=VPNRole(vpn_data['role']),
            listen_port=vpn_data.get('listen_port'),
            remote_host=vpn_data.get('remote_host'),
            remote_port=vpn_data.get('remote_port'),
            allowed_ips=vpn_data.get('allowed_ips', []),
            public_key_ref=_resolve_secret(vpn_data.get('public_key_ref'), secret_resolver),
            private_key_ref=_resolve_secret(vpn_data.get('private_key_ref'), secret_resolver),
            preshared_key_ref=_resolve_secret(vpn_data.get('preshared_key_ref'), secret_resolver)
        )
        vpn_list.append(vpn)
    
    # Parse Firewall
    firewall = None
    firewall_data = data.get('firewall')
    if firewall_data:
        rules = []
        for rule_data in firewall_data.get('rules', []):
            protocol_str = rule_data.get('protocol')
            protocol = Protocol(protocol_str) if protocol_str else None
            
            rule = FirewallRule(
                name=rule_data['name'],
                action=FirewallAction(rule_data['action']),
                from_zones=rule_data.get('from', []),
                to_zones=rule_data.get('to', []),
                protocol=protocol,
                port=rule_data.get('port'),
                comment=rule_data.get('comment')
            )
            rules.append(rule)
        
        default_policy_str = firewall_data.get('default_policy', 'drop')
        firewall = Firewall(
            default_policy=FirewallAction(default_policy_str),
            rules=rules
        )
    
    # Parse NAT
    nat = None
    nat_data = data.get('nat')
    if nat_data:
        port_forwards = []
        for pf_data in nat_data.get('port_forwards', []):
            pf = PortForward(
                name=pf_data['name'],
                external_port=pf_data['external_port'],
                internal_ip=pf_data['internal_ip'],
                internal_port=pf_data['internal_port'],
                protocol=pf_data.get('protocol', 'tcp')
            )
            port_forwards.append(pf)
        
        nat = NAT(
            masquerade=nat_data.get('masquerade', True),
            port_forwards=port_forwards
        )
    
    # Parse DNS
    dns = None
    dns_data = data.get('dns')
    if dns_data:
        static_records = []
        for record_data in dns_data.get('static_records', []):
            record = DNSRecord(
                name=record_data['name'],
                ip=record_data['ip']
            )
            static_records.append(record)
        
        dns = DNS(
            forwarders=dns_data.get('forwarders', []),
            local_domain=dns_data.get('local_domain'),
            static_records=static_records
        )
    
    return Policy(
        meta=meta,
        wan=wan,
        lans=lans,
        wifi=wifi_list,
        vpn=vpn_list,
        firewall=firewall,
        nat=nat,
        dns=dns
    )


def _resolve_secret(ref: Optional[str], resolver: Optional[SecretResolver]) -> Optional[str]:
    """Resolve a secret reference if resolver is provided."""
    if not ref or not resolver:
        return ref
    return resolver.resolve(ref)
