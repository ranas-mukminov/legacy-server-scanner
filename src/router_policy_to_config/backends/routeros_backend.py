"""
RouterOS backend - generates MikroTik RouterOS configuration scripts.

Supports RouterOS v6 and v7 syntax for:
- PPPoE, DHCP, and static WAN
- LANs with DHCP servers
- VLANs
- Wi-Fi (basic)
- VPN (WireGuard)
- Firewall rules
- NAT and port forwarding
"""

from typing import List
from ..model import Policy, LAN, WANType, VPNType, FirewallAction


class RouterOSBackend:
    """Generate RouterOS configuration from policy."""
    
    def __init__(self, version: str = "v7"):
        self.version = version
    
    def render(self, policy: Policy) -> str:
        """
        Render complete RouterOS configuration script.
        
        Returns:
            RouterOS script as string
        """
        lines = []
        
        # Header
        lines.append("# RouterOS Configuration Script")
        lines.append(f"# Generated from policy: {policy.meta.name}")
        if policy.meta.description:
            lines.append(f"# {policy.meta.description}")
        lines.append(f"# Target: RouterOS {self.version}")
        lines.append("")
        lines.append("# WARNING: Review this configuration before applying to production!")
        lines.append("")
        
        # WAN configuration
        lines.append("# === WAN Configuration ===")
        lines.extend(self._render_wan(policy))
        lines.append("")
        
        # LAN configuration
        lines.append("# === LAN Configuration ===")
        for lan in policy.lans:
            lines.extend(self._render_lan(lan))
            lines.append("")
        
        # Wi-Fi configuration
        if policy.wifi:
            lines.append("# === Wi-Fi Configuration ===")
            for wifi in policy.wifi:
                lines.extend(self._render_wifi(wifi, policy))
                lines.append("")
        
        # VPN configuration
        if policy.vpn:
            lines.append("# === VPN Configuration ===")
            for vpn in policy.vpn:
                lines.extend(self._render_vpn(vpn))
                lines.append("")
        
        # Firewall configuration
        if policy.firewall:
            lines.append("# === Firewall Configuration ===")
            lines.extend(self._render_firewall(policy))
            lines.append("")
        
        # NAT configuration
        if policy.nat:
            lines.append("# === NAT Configuration ===")
            lines.extend(self._render_nat(policy))
            lines.append("")
        
        # DNS configuration
        if policy.dns:
            lines.append("# === DNS Configuration ===")
            lines.extend(self._render_dns(policy))
            lines.append("")
        
        return "\n".join(lines)
    
    def _render_wan(self, policy: Policy) -> List[str]:
        """Render WAN configuration."""
        lines = []
        wan = policy.wan
        
        if wan.type == WANType.PPPOE:
            lines.append(f"# PPPoE WAN on {wan.interface}")
            lines.append(f"/interface pppoe-client")
            lines.append(f"add name=pppoe-out1 interface={wan.interface} \\")
            lines.append(f"    user=\"{wan.username or 'CHANGE_ME'}\" \\")
            lines.append(f"    password=\"{wan.password_ref or 'CHANGE_ME'}\" \\")
            if wan.mtu:
                lines.append(f"    max-mtu={wan.mtu} \\")
            lines.append(f"    disabled=no")
            
        elif wan.type == WANType.DHCP:
            lines.append(f"# DHCP WAN on {wan.interface}")
            lines.append(f"/ip dhcp-client")
            lines.append(f"add interface={wan.interface} disabled=no")
            
        elif wan.type == WANType.STATIC:
            lines.append(f"# Static WAN on {wan.interface}")
            lines.append(f"/ip address")
            lines.append(f"add address={wan.ip_address}/{self._netmask_to_cidr(wan.netmask or '255.255.255.0')} \\")
            lines.append(f"    interface={wan.interface}")
            lines.append(f"/ip route")
            lines.append(f"add gateway={wan.gateway}")
            
            if wan.dns:
                lines.append(f"/ip dns")
                dns_servers = ','.join(wan.dns)
                lines.append(f"set servers={dns_servers}")
        
        return lines
    
    def _render_lan(self, lan: LAN) -> List[str]:
        """Render LAN configuration."""
        lines = []
        bridge_name = f"bridge-{lan.name}"
        
        lines.append(f"# LAN: {lan.name}")
        
        # Create bridge
        lines.append(f"/interface bridge")
        lines.append(f"add name={bridge_name}")
        
        # Add IP address
        lines.append(f"/ip address")
        cidr = lan.subnet.split('/')[1] if '/' in lan.subnet else '24'
        lines.append(f"add address={lan.gateway}/{cidr} interface={bridge_name}")
        
        # VLAN configuration
        if lan.vlan_id:
            lines.append(f"# VLAN {lan.vlan_id} for {lan.name}")
            lines.append(f"/interface vlan")
            lines.append(f"add name=vlan{lan.vlan_id} vlan-id={lan.vlan_id} interface={bridge_name}")
        
        # DHCP server
        if lan.dhcp and lan.dhcp.enabled:
            pool_name = f"dhcp-pool-{lan.name}"
            lines.append(f"/ip pool")
            if lan.dhcp.range:
                start, end = lan.dhcp.range.split('-')
                lines.append(f"add name={pool_name} ranges={start.strip()}-{end.strip()}")
            else:
                lines.append(f"add name={pool_name} ranges={lan.subnet}")
            
            lines.append(f"/ip dhcp-server")
            lines.append(f"add name=dhcp-{lan.name} interface={bridge_name} \\")
            lines.append(f"    address-pool={pool_name} \\")
            if lan.dhcp.lease_time:
                lines.append(f"    lease-time={lan.dhcp.lease_time} \\")
            lines.append(f"    disabled=no")
            
            lines.append(f"/ip dhcp-server network")
            lines.append(f"add address={lan.subnet} gateway={lan.gateway}")
            
            if lan.dhcp.dns:
                dns_servers = ','.join(lan.dhcp.dns)
                lines.append(f"    dns-server={dns_servers}")
        
        return lines
    
    def _render_wifi(self, wifi, policy: Policy) -> List[str]:
        """Render Wi-Fi configuration (simplified for RouterOS)."""
        lines = []
        lines.append(f"# Wi-Fi: {wifi.name} ({wifi.ssid})")
        lines.append(f"# Note: Adjust interface name based on your hardware")
        lines.append(f"/interface wireless")
        lines.append(f"set [ find default-name=wlan1 ] \\")
        lines.append(f"    ssid=\"{wifi.ssid}\" \\")
        lines.append(f"    mode={wifi.mode.value} \\")
        
        if wifi.security.encryption.value != "open":
            lines.append(f"    security-profile=default \\")
            lines.append(f"    # Configure security profile separately")
        
        if wifi.hidden:
            lines.append(f"    hide-ssid=yes \\")
        
        lines.append(f"    disabled=no")
        
        return lines
    
    def _render_vpn(self, vpn) -> List[str]:
        """Render VPN configuration."""
        lines = []
        
        if vpn.type == VPNType.WIREGUARD:
            lines.append(f"# WireGuard VPN ({vpn.role.value})")
            lines.append(f"/interface wireguard")
            lines.append(f"add name=wireguard1 \\")
            if vpn.listen_port:
                lines.append(f"    listen-port={vpn.listen_port} \\")
            if vpn.private_key_ref:
                lines.append(f"    private-key=\"{vpn.private_key_ref}\" \\")
            lines.append(f"    disabled=no")
            
            if vpn.allowed_ips:
                lines.append(f"/interface wireguard peers")
                for ip in vpn.allowed_ips:
                    lines.append(f"add interface=wireguard1 allowed-address={ip}")
        
        return lines
    
    def _render_firewall(self, policy: Policy) -> List[str]:
        """Render firewall configuration."""
        lines = []
        
        lines.append("# Firewall filter rules")
        lines.append("/ip firewall filter")
        
        # Default established/related connections
        lines.append("add chain=input connection-state=established,related action=accept \\")
        lines.append("    comment=\"Allow established/related\"")
        
        lines.append("add chain=forward connection-state=established,related action=accept")
        
        # Custom rules
        for rule in policy.firewall.rules:
            chain = "forward"
            if any(zone in rule.to_zones for zone in [policy.wan.interface, "wan"]):
                chain = "forward"
            
            action = rule.action.value
            comment = rule.comment or rule.name
            
            lines.append(f"add chain={chain} action={action} \\")
            lines.append(f"    comment=\"{comment}\"")
        
        # Default drop
        if policy.firewall.default_policy == FirewallAction.DROP:
            lines.append("add chain=input action=drop comment=\"Drop all other input\"")
            lines.append("add chain=forward action=drop comment=\"Drop all other forward\"")
        
        return lines
    
    def _render_nat(self, policy: Policy) -> List[str]:
        """Render NAT configuration."""
        lines = []
        
        if policy.nat.masquerade:
            lines.append("# Masquerade NAT for WAN")
            lines.append("/ip firewall nat")
            wan_interface = "pppoe-out1" if policy.wan.type == WANType.PPPOE else policy.wan.interface
            lines.append(f"add chain=srcnat out-interface={wan_interface} action=masquerade")
        
        # Port forwarding
        for pf in policy.nat.port_forwards:
            lines.append(f"# Port forward: {pf.name}")
            protocol = pf.protocol if pf.protocol != "both" else "tcp,udp"
            lines.append(f"add chain=dstnat protocol={protocol} \\")
            lines.append(f"    dst-port={pf.external_port} \\")
            lines.append(f"    action=dst-nat to-addresses={pf.internal_ip} \\")
            lines.append(f"    to-ports={pf.internal_port}")
        
        return lines
    
    def _render_dns(self, policy: Policy) -> List[str]:
        """Render DNS configuration."""
        lines = []
        
        if policy.dns.forwarders:
            servers = ','.join(policy.dns.forwarders)
            lines.append(f"/ip dns")
            lines.append(f"set servers={servers} allow-remote-requests=yes")
        
        if policy.dns.static_records:
            lines.append(f"/ip dns static")
            for record in policy.dns.static_records:
                lines.append(f"add name={record.name} address={record.ip}")
        
        return lines
    
    @staticmethod
    def _netmask_to_cidr(netmask: str) -> str:
        """Convert netmask to CIDR notation."""
        netmask_map = {
            '255.255.255.0': '24',
            '255.255.255.128': '25',
            '255.255.255.192': '26',
            '255.255.255.224': '27',
            '255.255.255.240': '28',
            '255.255.255.248': '29',
            '255.255.255.252': '30',
            '255.255.0.0': '16',
            '255.0.0.0': '8',
        }
        return netmask_map.get(netmask, '24')
