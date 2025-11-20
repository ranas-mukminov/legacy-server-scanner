#!/usr/bin/env bash
set -euo pipefail

echo "Running ruff..."
ruff src tests

echo "Running mypy..."
mypy src

echo "Running yamllint..."
yamllint .

echo "Validating compose examples..."
python - <<'PY'
import yaml
from pathlib import Path
for path in Path('examples').rglob('*.yml*'):
    yaml.safe_load(Path(path).read_text())
print('YAML examples parsed OK')
PY
