from legacy_migration_assistant.legacy_server_scanner.cron import parse_crontab_text

CRON_SAMPLE = """
SHELL=/bin/bash
# comment line
*/5 * * * * /usr/bin/php /srv/app/artisan schedule:run
0 2 * * * /usr/bin/backup.sh
"""


def test_parse_crontab_text():
    jobs = parse_crontab_text(CRON_SAMPLE, source="user", user="root")
    assert len(jobs) == 2
    assert jobs[0].schedule.startswith("*/5")
