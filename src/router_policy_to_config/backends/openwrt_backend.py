"""
OpenWrt backend - generates OpenWrt UCI configuration files.

Generates UCI config files for:
- network (WAN, LANs, VLANs)
- wireless (Wi-Fi)
- firewall (zones, rules)
- dhcp (DHCP servers)
"""

from typing import Dict
from ..model import Policy, LAN, WANType, WiFiEncryption


class OpenWrtBackend:
    """Generate OpenWrt UCI configuration from policy."""
    
    def render(self, policy: Policy) -> Dict[str, str]:
        """
        Render OpenWrt UCI configuration files.
        
        Returns:
            Dictionary mapping filename to content
        """
        configs = {}
        
        # Generate network config
        configs['network'] = self._render_network(policy)
        
        # Generate wireless config
        if policy.wifi:
            configs['wireless'] = self._render_wireless(policy)
        
        # Generate firewall config
        if policy.firewall or policy.nat:
            configs['firewall'] = self._render_firewall(policy)
        
        # Generate DHCP config
        configs['dhcp'] = self._render_dhcp(policy)
        
        return configs
    
    def _render_network(self, policy: Policy) -> str:
        """Render /etc/config/network."""
        lines = []
        
        lines.append("# OpenWrt Network Configuration")
        lines.append(f"# Generated from policy: {policy.meta.name}")
        lines.append("")
        
        # Loopback interface
        lines.append("config interface 'loopback'")
        lines.append("\toption device 'lo'")
        lines.append("\toption proto 'static'")
        lines.append("\toption ipaddr '127.0.0.1'")
        lines.append("\toption netmask '255.255.255.0'")
        lines.append("")
        
        # WAN interface
        lines.append("# WAN Configuration")
        lines.append("config interface 'wan'")
        lines.append(f"\toption device '{policy.wan.interface}'")
        
        if policy.wan.type == WANType.PPPOE:
            lines.append("\toption proto 'pppoe'")
            lines.append(f"\toption username '{policy.wan.username or 'CHANGE_ME'}'")
            lines.append(f"\toption password '{policy.wan.password_ref or 'CHANGE_ME'}'")
            if policy.wan.mtu:
                lines.append(f"\toption mtu '{policy.wan.mtu}'")
        
        elif policy.wan.type == WANType.DHCP:
            lines.append("\toption proto 'dhcp'")
        
        elif policy.wan.type == WANType.STATIC:
            lines.append("\toption proto 'static'")
            lines.append(f"\toption ipaddr '{policy.wan.ip_address}'")
            lines.append(f"\toption netmask '{policy.wan.netmask or '255.255.255.0'}'")
            lines.append(f"\toption gateway '{policy.wan.gateway}'")
            if policy.wan.dns:
                dns_str = ' '.join(policy.wan.dns)
                lines.append(f"\toption dns '{dns_str}'")
        
        lines.append("")
        
        # LAN interfaces
        for lan in policy.lans:
            lines.extend(self._render_lan_interface(lan))
            lines.append("")
        
        return "\n".join(lines)
    
    def _render_lan_interface(self, lan: LAN) -> list:
        """Render a LAN interface configuration."""
        lines = []
        
        lines.append(f"# LAN: {lan.name}")
        lines.append(f"config interface '{lan.name}'")
        lines.append("\toption proto 'static'")
        lines.append(f"\toption ipaddr '{lan.gateway}'")
        
        # Extract netmask from subnet
        if '/' in lan.subnet:
            cidr = lan.subnet.split('/')[1]
            netmask = self._cidr_to_netmask(int(cidr))
            lines.append(f"\toption netmask '{netmask}'")
        
        if lan.vlan_id:
            lines.append(f"\toption type 'bridge'")
            lines.append(f"\toption ifname 'eth0.{lan.vlan_id}'")
        else:
            lines.append(f"\toption type 'bridge'")
            lines.append(f"\toption ifname 'eth0'")
        
        return lines
    
    def _render_wireless(self, policy: Policy) -> str:
        """Render /etc/config/wireless."""
        lines = []
        
        lines.append("# OpenWrt Wireless Configuration")
        lines.append(f"# Generated from policy: {policy.meta.name}")
        lines.append("")
        
        # Radio configuration (simplified - assumes one radio per band)
        radios = {}
        for wifi in policy.wifi:
            if wifi.band and wifi.band not in radios:
                radios[wifi.band] = wifi
        
        radio_idx = 0
        for band, wifi in radios.items():
            lines.append(f"config wifi-device 'radio{radio_idx}'")
            lines.append("\toption type 'mac80211'")
            
            if band == "2.4GHz":
                lines.append("\toption band '2g'")
                if wifi.channel:
                    lines.append(f"\toption channel '{wifi.channel}'")
                else:
                    lines.append("\toption channel 'auto'")
            elif band == "5GHz":
                lines.append("\toption band '5g'")
                if wifi.channel:
                    lines.append(f"\toption channel '{wifi.channel}'")
                else:
                    lines.append("\toption channel 'auto'")
            
            lines.append("\toption htmode 'HT20'")
            lines.append("\toption disabled '0'")
            lines.append("")
            radio_idx += 1
        
        # Wi-Fi interfaces
        for idx, wifi in enumerate(policy.wifi):
            lines.extend(self._render_wifi_interface(wifi, idx))
            lines.append("")
        
        return "\n".join(lines)
    
    def _render_wifi_interface(self, wifi, idx: int) -> list:
        """Render a Wi-Fi interface configuration."""
        lines = []
        
        lines.append(f"# Wi-Fi: {wifi.name}")
        lines.append(f"config wifi-iface 'wifinet{idx}'")
        
        # Determine radio based on band
        radio = 0
        if wifi.band == "5GHz":
            radio = 1
        
        lines.append(f"\toption device 'radio{radio}'")
        lines.append(f"\toption network '{wifi.lan}'")
        lines.append(f"\toption mode 'ap'")
        lines.append(f"\toption ssid '{wifi.ssid}'")
        
        # Encryption
        enc = wifi.security.encryption
        if enc == WiFiEncryption.OPEN:
            lines.append("\toption encryption 'none'")
        elif enc == WiFiEncryption.WPA2_PSK:
            lines.append("\toption encryption 'psk2'")
            lines.append(f"\toption key '{wifi.security.password_ref or 'CHANGE_ME'}'")
        elif enc == WiFiEncryption.WPA3_SAE:
            lines.append("\toption encryption 'sae'")
            lines.append(f"\toption key '{wifi.security.password_ref or 'CHANGE_ME'}'")
        
        if wifi.hidden:
            lines.append("\toption hidden '1'")
        
        if wifi.guest:
            lines.append("\toption isolate '1'")
        
        return lines
    
    def _render_firewall(self, policy: Policy) -> str:
        """Render /etc/config/firewall."""
        lines = []
        
        lines.append("# OpenWrt Firewall Configuration")
        lines.append(f"# Generated from policy: {policy.meta.name}")
        lines.append("")
        
        # Defaults
        lines.append("config defaults")
        lines.append("\toption input 'REJECT'")
        lines.append("\toption output 'ACCEPT'")
        
        if policy.firewall:
            default = policy.firewall.default_policy.value.upper()
            lines.append(f"\toption forward '{default}'")
        else:
            lines.append("\toption forward 'REJECT'")
        
        lines.append("\toption synflood_protect '1'")
        lines.append("")
        
        # WAN zone
        lines.append("# WAN Zone")
        lines.append("config zone")
        lines.append("\toption name 'wan'")
        lines.append("\tlist network 'wan'")
        lines.append("\toption input 'REJECT'")
        lines.append("\toption output 'ACCEPT'")
        lines.append("\toption forward 'REJECT'")
        lines.append("\toption masq '1'")
        lines.append("\toption mtu_fix '1'")
        lines.append("")
        
        # LAN zones
        for lan in policy.lans:
            lines.extend(self._render_firewall_zone(lan, policy))
            lines.append("")
        
        # Forwarding rules
        lines.append("# Zone forwarding")
        for lan in policy.lans:
            if not lan.isolated_from or 'wan' not in lan.isolated_from:
                lines.append("config forwarding")
                lines.append(f"\toption src '{lan.name}'")
                lines.append("\toption dest 'wan'")
                lines.append("")
        
        # Custom rules
        if policy.firewall:
            for rule in policy.firewall.rules:
                lines.extend(self._render_firewall_rule(rule))
                lines.append("")
        
        # Port forwards
        if policy.nat and policy.nat.port_forwards:
            for pf in policy.nat.port_forwards:
                lines.append(f"# Port forward: {pf.name}")
                lines.append("config redirect")
                lines.append(f"\toption name '{pf.name}'")
                lines.append("\toption src 'wan'")
                lines.append(f"\toption proto '{pf.protocol}'")
                lines.append(f"\toption src_dport '{pf.external_port}'")
                lines.append(f"\toption dest_ip '{pf.internal_ip}'")
                lines.append(f"\toption dest_port '{pf.internal_port}'")
                lines.append("\toption target 'DNAT'")
                lines.append("")
        
        return "\n".join(lines)
    
    def _render_firewall_zone(self, lan: LAN, policy: Policy) -> list:
        """Render firewall zone for a LAN."""
        lines = []
        
        lines.append(f"# Zone: {lan.name}")
        lines.append("config zone")
        lines.append(f"\toption name '{lan.name}'")
        lines.append(f"\tlist network '{lan.name}'")
        lines.append("\toption input 'ACCEPT'")
        lines.append("\toption output 'ACCEPT'")
        
        if lan.isolated_from:
            lines.append("\toption forward 'REJECT'")
        else:
            lines.append("\toption forward 'ACCEPT'")
        
        return lines
    
    def _render_firewall_rule(self, rule) -> list:
        """Render a firewall rule."""
        lines = []
        
        lines.append(f"# Rule: {rule.name}")
        lines.append("config rule")
        lines.append(f"\toption name '{rule.name}'")
        
        if rule.from_zones:
            for zone in rule.from_zones:
                lines.append(f"\tlist src '{zone}'")
        
        if rule.to_zones:
            for zone in rule.to_zones:
                lines.append(f"\tlist dest '{zone}'")
        
        if rule.protocol:
            lines.append(f"\toption proto '{rule.protocol.value}'")
        
        if rule.port:
            lines.append(f"\toption dest_port '{rule.port}'")
        
        action = rule.action.value.upper()
        lines.append(f"\toption target '{action}'")
        
        return lines
    
    def _render_dhcp(self, policy: Policy) -> str:
        """Render /etc/config/dhcp."""
        lines = []
        
        lines.append("# OpenWrt DHCP Configuration")
        lines.append(f"# Generated from policy: {policy.meta.name}")
        lines.append("")
        
        # Global dnsmasq config
        lines.append("config dnsmasq")
        lines.append("\toption domainneeded '1'")
        lines.append("\toption boguspriv '1'")
        lines.append("\toption filterwin2k '0'")
        lines.append("\toption localise_queries '1'")
        lines.append("\toption rebind_protection '1'")
        lines.append("\toption rebind_localhost '1'")
        lines.append("\toption local '/lan/'")
        lines.append("\toption domain 'lan'")
        lines.append("\toption expandhosts '1'")
        lines.append("\toption nonegcache '0'")
        lines.append("\toption authoritative '1'")
        lines.append("\toption readethers '1'")
        lines.append("\toption leasefile '/tmp/dhcp.leases'")
        lines.append("\toption resolvfile '/tmp/resolv.conf.d/resolv.conf.auto'")
        lines.append("")
        
        # DHCP pools for LANs
        for lan in policy.lans:
            if lan.dhcp and lan.dhcp.enabled:
                lines.extend(self._render_dhcp_pool(lan))
                lines.append("")
        
        # DNS configuration
        if policy.dns:
            if policy.dns.forwarders:
                for server in policy.dns.forwarders:
                    lines.append("config server")
                    lines.append(f"\toption server '{server}'")
                    lines.append("")
        
        return "\n".join(lines)
    
    def _render_dhcp_pool(self, lan: LAN) -> list:
        """Render DHCP pool for a LAN."""
        lines = []
        
        lines.append(f"# DHCP for {lan.name}")
        lines.append(f"config dhcp '{lan.name}'")
        lines.append(f"\toption interface '{lan.name}'")
        lines.append("\toption start '100'")
        lines.append("\toption limit '150'")
        
        if lan.dhcp.lease_time:
            lines.append(f"\toption leasetime '{lan.dhcp.lease_time}'")
        else:
            lines.append("\toption leasetime '12h'")
        
        if lan.dhcp.dns:
            dns_list = ' '.join(lan.dhcp.dns)
            lines.append(f"\tlist dhcp_option '6,{dns_list}'")
        
        return lines
    
    @staticmethod
    def _cidr_to_netmask(cidr: int) -> str:
        """Convert CIDR to netmask."""
        cidr_map = {
            8: '255.0.0.0',
            16: '255.255.0.0',
            24: '255.255.255.0',
            25: '255.255.255.128',
            26: '255.255.255.192',
            27: '255.255.255.224',
            28: '255.255.255.240',
            29: '255.255.255.248',
            30: '255.255.255.252',
        }
        return cidr_map.get(cidr, '255.255.255.0')
