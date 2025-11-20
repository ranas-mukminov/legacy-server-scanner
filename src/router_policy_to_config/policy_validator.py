"""
Semantic policy validation.

Validates policy beyond schema checks (e.g., subnet overlaps, consistency).
"""

import ipaddress
from typing import List
from .model import Policy, LAN, WANType


class ValidationError(Exception):
    """Exception raised for validation errors."""
    pass


def validate_policy(policy: Policy) -> List[str]:
    """
    Validate policy for semantic correctness.
    
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    # Validate WAN configuration
    errors.extend(_validate_wan(policy))
    
    # Validate LAN configuration
    errors.extend(_validate_lans(policy))
    
    # Validate Wi-Fi configuration
    errors.extend(_validate_wifi(policy))
    
    # Validate VPN configuration
    errors.extend(_validate_vpn(policy))
    
    # Validate firewall configuration
    errors.extend(_validate_firewall(policy))
    
    return errors


def _validate_wan(policy: Policy) -> List[str]:
    """Validate WAN configuration."""
    errors = []
    wan = policy.wan
    
    if wan.type == WANType.PPPOE:
        if not wan.username:
            errors.append("WAN: PPPoE requires username")
        if not wan.password_ref:
            errors.append("WAN: PPPoE requires password_ref")
    
    elif wan.type == WANType.STATIC:
        if not wan.ip_address:
            errors.append("WAN: Static type requires ip_address")
        if not wan.netmask:
            errors.append("WAN: Static type requires netmask")
        if not wan.gateway:
            errors.append("WAN: Static type requires gateway")
    
    return errors


def _validate_lans(policy: Policy) -> List[str]:
    """Validate LAN configurations."""
    errors = []
    
    if not policy.lans:
        errors.append("At least one LAN must be defined")
        return errors
    
    # Check for duplicate LAN names
    lan_names = [lan.name for lan in policy.lans]
    duplicates = [name for name in lan_names if lan_names.count(name) > 1]
    if duplicates:
        errors.append(f"Duplicate LAN names: {', '.join(set(duplicates))}")
    
    # Check for subnet overlaps
    networks = []
    for lan in policy.lans:
        try:
            network = ipaddress.IPv4Network(lan.subnet, strict=False)
            networks.append((lan.name, network))
            
            # Validate gateway is in subnet
            gateway_ip = ipaddress.IPv4Address(lan.gateway)
            if gateway_ip not in network:
                errors.append(f"LAN '{lan.name}': Gateway {lan.gateway} not in subnet {lan.subnet}")
            
            # Validate DHCP range
            if lan.dhcp and lan.dhcp.enabled and lan.dhcp.range:
                parts = lan.dhcp.range.split('-')
                if len(parts) == 2:
                    try:
                        start_ip = ipaddress.IPv4Address(parts[0].strip())
                        end_ip = ipaddress.IPv4Address(parts[1].strip())
                        
                        if start_ip not in network:
                            errors.append(f"LAN '{lan.name}': DHCP range start {start_ip} not in subnet")
                        if end_ip not in network:
                            errors.append(f"LAN '{lan.name}': DHCP range end {end_ip} not in subnet")
                        if start_ip >= end_ip:
                            errors.append(f"LAN '{lan.name}': DHCP range start must be less than end")
                    except ValueError as e:
                        errors.append(f"LAN '{lan.name}': Invalid DHCP range IP: {e}")
                else:
                    errors.append(f"LAN '{lan.name}': Invalid DHCP range format (use x.x.x.x-y.y.y.y)")
        
        except ValueError as e:
            errors.append(f"LAN '{lan.name}': Invalid subnet {lan.subnet}: {e}")
    
    # Check for overlapping subnets
    for i, (name1, net1) in enumerate(networks):
        for name2, net2 in networks[i+1:]:
            if net1.overlaps(net2):
                errors.append(f"LANs '{name1}' and '{name2}' have overlapping subnets")
    
    # Validate isolated_from references
    for lan in policy.lans:
        for isolated_name in lan.isolated_from:
            if isolated_name not in lan_names:
                errors.append(f"LAN '{lan.name}': References non-existent LAN '{isolated_name}' in isolated_from")
    
    # Validate VLAN IDs
    vlan_ids = [lan.vlan_id for lan in policy.lans if lan.vlan_id]
    duplicate_vlans = [vid for vid in vlan_ids if vlan_ids.count(vid) > 1]
    if duplicate_vlans:
        errors.append(f"Duplicate VLAN IDs: {', '.join(map(str, set(duplicate_vlans)))}")
    
    return errors


def _validate_wifi(policy: Policy) -> List[str]:
    """Validate Wi-Fi configurations."""
    errors = []
    
    lan_names = [lan.name for lan in policy.lans]
    wifi_names = []
    
    for wifi in policy.wifi:
        wifi_names.append(wifi.name)
        
        # Validate LAN reference
        if wifi.lan not in lan_names:
            errors.append(f"Wi-Fi '{wifi.name}': References non-existent LAN '{wifi.lan}'")
        
        # Validate security
        if wifi.security.encryption != "open" and not wifi.security.password_ref:
            errors.append(f"Wi-Fi '{wifi.name}': Encrypted network requires password_ref")
        
        # Validate channel
        if wifi.channel:
            if wifi.band == "2.4GHz" and wifi.channel > 14:
                errors.append(f"Wi-Fi '{wifi.name}': Invalid 2.4GHz channel {wifi.channel}")
            elif wifi.band == "5GHz" and wifi.channel not in range(36, 166):
                errors.append(f"Wi-Fi '{wifi.name}': Invalid 5GHz channel {wifi.channel}")
    
    # Check for duplicate Wi-Fi names
    duplicates = [name for name in wifi_names if wifi_names.count(name) > 1]
    if duplicates:
        errors.append(f"Duplicate Wi-Fi names: {', '.join(set(duplicates))}")
    
    return errors


def _validate_vpn(policy: Policy) -> List[str]:
    """Validate VPN configurations."""
    errors = []
    
    for i, vpn in enumerate(policy.vpn):
        vpn_id = f"VPN #{i+1}"
        
        if vpn.role.value == "server" and not vpn.listen_port:
            errors.append(f"{vpn_id}: Server role requires listen_port")
        
        if vpn.role.value == "client":
            if not vpn.remote_host:
                errors.append(f"{vpn_id}: Client role requires remote_host")
            if not vpn.remote_port:
                errors.append(f"{vpn_id}: Client role requires remote_port")
        
        # Validate allowed IPs
        for ip_cidr in vpn.allowed_ips:
            try:
                ipaddress.IPv4Network(ip_cidr, strict=False)
            except ValueError as e:
                errors.append(f"{vpn_id}: Invalid allowed IP '{ip_cidr}': {e}")
    
    return errors


def _validate_firewall(policy: Policy) -> List[str]:
    """Validate firewall configuration."""
    errors = []
    
    if not policy.firewall:
        return errors
    
    lan_names = [lan.name for lan in policy.lans]
    rule_names = []
    
    for rule in policy.firewall.rules:
        rule_names.append(rule.name)
        
        # Validate zone references
        for zone in rule.from_zones + rule.to_zones:
            if zone not in ['wan', 'vpn'] and not zone.startswith('192.') and zone not in lan_names:
                errors.append(f"Firewall rule '{rule.name}': Unknown zone '{zone}'")
        
        # Validate port with protocol
        if rule.port and not rule.protocol:
            errors.append(f"Firewall rule '{rule.name}': Port specified but protocol is missing")
    
    # Check for duplicate rule names
    duplicates = [name for name in rule_names if rule_names.count(name) > 1]
    if duplicates:
        errors.append(f"Duplicate firewall rule names: {', '.join(set(duplicates))}")
    
    return errors
