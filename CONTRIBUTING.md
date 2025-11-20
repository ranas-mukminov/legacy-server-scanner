# Contributing

Thanks for helping improve Legacy Migration Assistant!

## How to contribute
- Open an issue to discuss significant changes before starting.
- Keep PRs focused and include tests where relevant.
- Use type hints and avoid logging secrets or private data.
- Follow repository layout and naming; new modules go under `src/legacy_migration_assistant/`.

## Development setup
- Python 3.10+.
- Install dev deps: `pip install -e .[dev]`.
- Run checks: `scripts/lint.sh` and `pytest`.

## Code style
- Ruff for linting, 100-char lines, argparse-based CLIs.
- Prefer dataclasses/pydantic models for structured data.
- Keep shell interactions minimal and safe; allow injecting test fixtures to avoid real system changes.

## Commit messages
- Short imperative subject, details in the body when needed.

## Security
- No hardcoded secrets or tokens. Pass credentials only via environment when required.
- Report security concerns via issues; do not include exploits or confidential data.
