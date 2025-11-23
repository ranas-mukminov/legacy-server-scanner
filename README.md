# Legacy Migration Assistant 🔄

![CI](https://github.com/ranas-mukminov/legacy-migration-assistant/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)

🇬🇧 English | 🇷🇺 [Русская версия](README.ru.md)

## Overview

**Legacy Migration Assistant** is a command-line toolkit designed to audit legacy Linux servers and automatically generate Docker Compose and Kubernetes manifests. It scans installed packages, running services, open ports, cron jobs, and configuration files, then builds an application topology map and generates deployment blueprints with security-hardened defaults.

This tool is aimed at DevOps engineers, system administrators, and freelance integrators who need to containerize and migrate legacy infrastructure to modern platforms like Docker, K3s, or Kubernetes without manually documenting every component.

## Key Features

- **Automated server inventory** – Scans packages, systemd services, ports, cron jobs, and configs
- **Application topology mapping** – Automatically builds component relationships and dependencies
- **Docker Compose generation** – Creates ready-to-use `docker-compose.yaml` from topology maps
- **Kubernetes manifest generation** – Produces K8s Deployments, Services, Ingress, PVCs with security contexts
- **Security-hardened defaults** – Applies sensible resource limits, probes, and `securityContext` settings
- **Read-only scanning** – No modifications to the legacy server during the scan process
- **Extensible architecture** – Designed to support custom classifiers and AI-assisted topology refinement

## Architecture / Components

The toolkit consists of two main CLI tools:

1. **`legacy-scan`** – Server scanner that collects raw data and generates topology maps and Docker Compose files
   - **Scanner modules**: packages, services, ports, cron, configs
   - **Topology builder**: analyzes dependencies and builds component graph
   - **Compose generator**: produces Docker Compose YAML from topology

2. **`legacy-k8s`** – Kubernetes manifest generator that transforms application maps or Docker Compose into K8s resources
   - **Compose parser**: reads Docker Compose and extracts service definitions
   - **K8s generator**: creates Deployment, Service, Ingress, PVC manifests
   - **Resource advisor**: assigns CPU/memory requests and limits
   - **Security policies**: injects best-practice `securityContext`, probes, and network policies

**Data flow:**

```
Legacy Server → [legacy-scan scan] → scan.json
scan.json → [legacy-scan map] → app-map.yaml
app-map.yaml → [legacy-scan compose] → docker-compose.yaml
docker-compose.yaml → [legacy-k8s from-compose] → K8s manifests/
```

## Requirements

### Operating System
- **Linux distributions**: Ubuntu 20.04+, Debian 11+, RHEL 8+, Rocky Linux, AlmaLinux, or similar
- **Python version**: 3.10 or higher

### Privileges
- **Scanner** (`legacy-scan`): root or sudo access recommended for full system inventory
- **Generator** (`legacy-k8s`): no elevated privileges required

### Disk Space
- Minimal: ~50 MB for installation
- Scanning output: typically 1–10 MB per server

### Network
- Internet access required for pip installation
- No outbound connections during scanning (works offline after installation)

## Quick Start (TL;DR)

1. **Clone the repository and install**:
   ```bash
   git clone https://github.com/ranas-mukminov/legacy-migration-assistant.git
   cd legacy-migration-assistant
   pip install .
   ```

2. **Scan the legacy server**:
   ```bash
   sudo legacy-scan scan --output scan.json
   legacy-scan map --scan scan.json --output app-map.yaml
   legacy-scan compose --map app-map.yaml --output docker-compose.yaml
   ```

3. **Generate Kubernetes manifests** (on your workstation):
   ```bash
   legacy-k8s from-compose --compose docker-compose.yaml --output-dir k8s/ --namespace production --ingress-host example.com
   ```

4. **Review and deploy**:
   - Carefully review `docker-compose.yaml` and `k8s/*.yaml`
   - Replace placeholder secrets and environment variables
   - Test in a local or staging environment before production

## Detailed Installation

### Install from source (recommended)

1. **Ensure Python 3.10+ is installed**:
   ```bash
   python3 --version  # Should be 3.10 or higher
   ```

2. **Clone the repository**:
   ```bash
   git clone https://github.com/ranas-mukminov/legacy-migration-assistant.git
   cd legacy-migration-assistant
   ```

3. **Install the package**:
   ```bash
   pip install .
   ```

4. **Verify installation**:
   ```bash
   legacy-scan --help
   legacy-k8s --help
   ```

### Install with development dependencies

For contributors or those who want to run tests and linters:

```bash
pip install -e .[dev]
```

This installs additional tools: `pytest`, `ruff`, `mypy`, `bandit`, `yamllint`, and `pip-audit`.

## Configuration

### Scanner Configuration

The `legacy-scan` tool does not require a configuration file. All options are passed via CLI arguments:

```bash
legacy-scan scan --output scan.json
legacy-scan map --scan scan.json --output app-map.yaml
legacy-scan compose --map app-map.yaml --output docker-compose.yaml
```

### Kubernetes Generator Configuration

The `legacy-k8s` tool accepts the following options:

```bash
legacy-k8s from-compose \
  --compose docker-compose.yaml \
  --output-dir k8s/ \
  --namespace <YOUR_NAMESPACE> \
  --ingress-host <YOUR_DOMAIN>
```

**Environment variables** are not currently used for configuration, but secrets should be managed externally (e.g., Kubernetes Secrets, HashiCorp Vault).

### Sample Application Map

Application maps are YAML files describing components and their relationships. Example:

```yaml
components:
  - name: web
    component_type: web
    ports: [80, 443]
    volumes: [/var/www/html]
    environment: {}
    depends_on: [db]
    notes:
      - nginx detected
  - name: db
    component_type: database
    ports: [3306]
    volumes: [/var/lib/mysql]
    environment: {}
    depends_on: []
    notes:
      - mysql storage
relations:
  - source: web
    target: db
    description: web connects to db
packages: []
services: []
ports: []
cron: []
configs: []
```

## Usage & Common Tasks

### Scan a Legacy Server

1. **Log in to the legacy server** (SSH or direct access)
2. **Install the tool** (see [Detailed Installation](#detailed-installation))
3. **Run the scanner**:
   ```bash
   sudo legacy-scan scan --output scan.json
   ```
   This creates `scan.json` with packages, services, ports, cron, and configs.

### Build an Application Map

```bash
legacy-scan map --scan scan.json --output app-map.yaml
```

This produces a structured YAML file with components, dependencies, and notes.

### Generate Docker Compose

```bash
legacy-scan compose --map app-map.yaml --output docker-compose.yaml
```

Review the generated `docker-compose.yaml` and adjust image tags, secrets, and environment variables.

### Generate Kubernetes Manifests

```bash
legacy-k8s from-compose --compose docker-compose.yaml --output-dir k8s/ --namespace production --ingress-host <YOUR_DOMAIN>
```

This creates Deployment, Service, PersistentVolumeClaim, and Ingress manifests in the `k8s/` directory.

### Customize Generated Manifests

- **Secrets**: Replace placeholder values with Kubernetes Secrets or environment variable references
- **Resource limits**: Adjust CPU and memory requests/limits based on actual load
- **Probes**: Refine `livenessProbe` and `readinessProbe` for your application
- **Storage**: Configure StorageClass and volume sizes for PersistentVolumeClaims

## Update / Upgrade

To update the tool to the latest version:

```bash
cd legacy-migration-assistant
git pull origin main
pip install --upgrade .
```

If you installed with `-e` (editable mode), simply pull the latest changes:

```bash
git pull origin main
```

### Breaking Changes

Check `CHANGELOG.md` for version-specific breaking changes. The tool is currently in **0.1.0** (initial scaffold), so the API may change in future releases.

## Logs, Monitoring, Troubleshooting

### Logs

- **Scanner logs**: The tool outputs to `stdout` and `stderr`. Redirect to a file if needed:
  ```bash
  sudo legacy-scan scan --output scan.json > scanner.log 2>&1
  ```

- **Generated manifests**: Review YAML files directly; no runtime logs are generated by the tools themselves.

### Common Issues

| Problem | Solution |
|---------|----------|
| `Permission denied` when scanning | Run `legacy-scan scan` with `sudo` or as root |
| `Command not found: legacy-scan` | Ensure `pip install .` completed successfully and `~/.local/bin` is in your `PATH` |
| Missing packages in scan output | Some packages may be undetected if installed outside standard package managers |
| Docker Compose services missing dependencies | Manually review and edit `depends_on` in `docker-compose.yaml` |
| Kubernetes manifests missing Ingress | Provide `--ingress-host` flag when running `legacy-k8s from-compose` |
| Out-of-date Python version | Install Python 3.10+ using your distribution's package manager or pyenv |

### Debugging

Enable verbose output (if implemented in future versions):

```bash
legacy-scan scan --output scan.json --verbose
```

For now, inspect intermediate files (`scan.json`, `app-map.yaml`) to diagnose issues.

## Security Notes

### General Security Practices

- **Change default passwords**: Never use placeholder passwords in production
- **Protect secrets**: Use Kubernetes Secrets, HashiCorp Vault, or similar tools
- **Restrict access**: Do not expose port 22, 3306, or other sensitive ports directly to the Internet
- **Use TLS**: Enable TLS/SSL for web services and databases
- **Network policies**: Apply Kubernetes NetworkPolicies to limit pod-to-pod traffic

### Scanner Security

- The scanner **does not modify** the legacy server; it only reads system state
- **No credentials are logged** in scan output; however, config file paths are recorded
- Review `scan.json` and `app-map.yaml` before sharing to ensure no sensitive data is leaked

### Kubernetes Security

Generated manifests include:

- `securityContext` with `runAsNonRoot: true` and `allowPrivilegeEscalation: false`
- `readOnlyRootFilesystem: true` where applicable
- Resource requests and limits to prevent runaway containers
- Health probes to ensure application availability

**Always review and test manifests in a staging environment before production deployment.**

## Project Structure

```
legacy-migration-assistant/
├── src/
│   └── legacy_migration_assistant/
│       ├── legacy_server_scanner/     # Scanner modules
│       ├── legacy_to_k8s_blueprints/  # K8s generator modules
│       ├── router_policy_to_config/   # Router config generator (bonus)
│       └── core/                       # Shared models
├── tests/                              # Unit and integration tests
├── examples/                           # Sample YAML files
│   ├── maps/                          # Application topology examples
│   ├── compose/                       # Docker Compose examples
│   └── k8s/                           # Kubernetes manifest examples
├── scripts/                            # Lint, security, performance scripts
├── pyproject.toml                      # Python package configuration
├── CHANGELOG.md                        # Version history
├── CONTRIBUTING.md                     # Contribution guidelines
├── LEGAL.md                            # Legal disclaimers and usage terms
└── LICENSE                             # Apache 2.0 license
```

## Roadmap / Plans

### Planned Features

- **AI-assisted topology refinement**: Suggest component types and dependencies using LLMs
- **Additional platform support**: FreeBSD, Alpine Linux
- **Enhanced security scanning**: Detect outdated packages and CVEs
- **Multi-server orchestration**: Scan multiple servers and merge topology maps
- **Prometheus exporter**: Export scan results as Prometheus metrics
- **Grafana dashboard**: Visualize legacy infrastructure inventory

### Known Limitations

- Currently supports systemd-based distributions (Ubuntu, Debian, RHEL, etc.)
- SysVinit and upstart services are not yet fully supported
- Router policy features are experimental and may change

See [GitHub Issues](https://github.com/ranas-mukminov/legacy-migration-assistant/issues) for active feature requests and bug reports.

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Open an issue** to discuss significant changes before starting
2. **Keep PRs focused** and include tests where relevant
3. **Use type hints** and follow PEP 8 style
4. **Run linters** before submitting:
   ```bash
   bash scripts/lint.sh
   pytest
   ```

### Development Setup

```bash
git clone https://github.com/ranas-mukminov/legacy-migration-assistant.git
cd legacy-migration-assistant
pip install -e .[dev]
```

### Code Style

- **Linter**: Ruff (100-character line limit)
- **Type checker**: mypy
- **Testing**: pytest
- **CLI framework**: argparse

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

This project is licensed under the **Apache License 2.0**. See [LICENSE](LICENSE) for full terms.

## Author and Commercial Support

**Author**: [Ranas Mukminov](https://github.com/ranas-mukminov)

For production-grade deployments, infrastructure audits, migration consulting, and ongoing DevOps/SRE support, visit **[run-as-daemon.ru](https://run-as-daemon.ru)** (Russian) or contact the author via the GitHub profile.

Commercial services include:

- Legacy server audits and migration planning
- Docker and Kubernetes infrastructure design
- CI/CD pipeline setup and automation
- Monitoring, logging, and alerting solutions (Prometheus, Grafana, Loki)
- Security hardening and compliance consulting

---

**Always review, test, and validate configurations in a safe environment before applying to production systems.**
