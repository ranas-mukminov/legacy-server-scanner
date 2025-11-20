import textwrap

from legacy_migration_assistant.legacy_server_scanner.os_detection import detect_os_family, detect_os_release
from legacy_migration_assistant.core.models import OSFamily


def test_detect_os_family_debian():
    data = textwrap.dedent(
        """
        ID=debian
        VERSION_ID=11
        PRETTY_NAME="Debian GNU/Linux 11 (bullseye)"
        """
    )
    assert detect_os_family(data) == OSFamily.DEBIAN
    release = detect_os_release(data)
    assert release and release.id == "debian" and release.version_id == "11"


def test_detect_os_family_rhel():
    data = textwrap.dedent(
        """
        ID="centos"
        VERSION_ID="8"
        """
    )
    assert detect_os_family(data) == OSFamily.RHEL
