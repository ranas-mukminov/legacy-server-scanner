from legacy_migration_assistant.legacy_server_scanner.ports import (
    parse_netstat_output,
    parse_ss_output,
)

SS_SAMPLE = """
Netid State  Recv-Q Send-Q Local Address:Port Peer Address:Port Process
udp   UNCONN 0      0      0.0.0.0:68      0.0.0.0:*    users:(""(dhclient,1234,5))
tcp   LISTEN 0      128    0.0.0.0:80      0.0.0.0:*    users:(""(nginx,4321,5))
"""

NETSTAT_SAMPLE = """
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State
udp        0      0 0.0.0.0:68              0.0.0.0:*
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN
"""


def test_parse_ss_output():
    ports = parse_ss_output(SS_SAMPLE)
    assert any(p.port == 80 and p.protocol == "tcp" for p in ports)


def test_parse_netstat_output():
    ports = parse_netstat_output(NETSTAT_SAMPLE)
    assert any(p.port == 22 for p in ports)
