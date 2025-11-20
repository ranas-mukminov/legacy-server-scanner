from legacy_migration_assistant.legacy_server_scanner.services import (
    parse_ps_aux,
    parse_systemctl_list_units,
)

SYSTEMCTL_SAMPLE = """
  UNIT                            LOAD   ACTIVE SUB     DESCRIPTION
  cron.service                    loaded active running Regular background program processing daemon
  nginx.service                   loaded active running A high performance web server
"""

PS_SAMPLE = """
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.1 169040  8796 ?        Ss   09:14   0:03 /sbin/init
daemon     222  0.0  0.0  12000   900 ?        Ss   09:14   0:00 /usr/sbin/cron -f
"""


def test_parse_systemctl():
    services = parse_systemctl_list_units(SYSTEMCTL_SAMPLE)
    assert any(s.name == "nginx" for s in services)
    assert services[0].manager == "systemd"


def test_parse_ps_aux():
    services = parse_ps_aux(PS_SAMPLE)
    assert any(s.name == "cron" for s in services)
    assert services[0].pid is not None
