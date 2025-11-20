from legacy_migration_assistant.legacy_server_scanner.packages import (
    parse_dpkg_output,
    parse_rpm_output,
)

DPKG_SAMPLE = """
Desired=Unknown/Install/Remove/Purge/Hold
| Status=Not/Inst/Conf-files/Unpacked/halF-conf/Half-inst/trig-aWait/Trig-pend
|/ Err?=(none)/Reinst-required (Status,Err: uppercase=bad)
||/ Name           Version        Architecture Description
ii  bash           5.1-2ubuntu7.1 amd64        GNU Bourne Again SHell
ii  nginx          1.18.0-10      amd64        small, powerful web server
"""

RPM_SAMPLE = """
bash-5.2.15-1.el9.x86_64
nginx-1.20.1-14.el9.x86_64
"""


def test_parse_dpkg_output():
    packages = parse_dpkg_output(DPKG_SAMPLE)
    assert any(p.name == "nginx" for p in packages)
    assert any(p.version.startswith("5.1") for p in packages if p.name == "bash")


def test_parse_rpm_output():
    packages = parse_rpm_output(RPM_SAMPLE)
    assert {p.name for p in packages} == {"bash", "nginx"}
