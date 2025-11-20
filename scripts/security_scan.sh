#!/usr/bin/env bash
set -euo pipefail

pip-audit || true
bandit -r src || true
