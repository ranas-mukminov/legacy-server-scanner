# router-policy-to-config

![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![CI](https://github.com/ranas-mukminov/legacy-server-scanner/actions/workflows/ci.yml/badge.svg)

## English

### What is this?

**router-policy-to-config** is an AI-assisted copilot for router configuration that transforms high-level YAML policies into vendor-specific router configurations. Instead of manually writing low-level commands, you define your network intent once and generate configurations for:

- **MikroTik RouterOS** (v6/v7) - scripts and exports
- **OpenWrt** - UCI configuration files

The tool also provides:
- **Diff engine** - Compare generated configs against existing router configurations
- **Test lab** - Docker/QEMU-based RouterOS and OpenWrt environments for safe testing
- **AI helpers** - Convert natural language descriptions to YAML policies

### Supported Platforms

- **RouterOS** (MikroTik) - PPPoE, static/DHCP WAN, firewall, VLANs, Wi-Fi, VPN
- **OpenWrt** - UCI-based configuration for network, wireless, firewall, and DHCP

### Why?

Today, most network administrators configure routers by:
- Using **Winbox or CLI** on MikroTik RouterOS with complex, low-level commands
- Editing **LuCI web interface** or manually modifying UCI files on OpenWrt
- Maintaining separate, incompatible configurations for different vendors

**router-policy-to-config** solves this by providing:
- **Vendor-neutral policy format** - Define your network intent once in YAML
- **Automated generation** - Convert policy to RouterOS scripts or OpenWrt UCI configs
- **Safe validation** - Test in local lab before applying to production routers
- **Version control** - Track network policies in Git like infrastructure-as-code

### Features

✅ **YAML Policy Language**
- Define WAN (PPPoE, DHCP, static), LANs, guest networks
- Configure Wi-Fi with WPA2/WPA3 security
- Set up VPN (WireGuard, L2TP, IPsec)
- Declare firewall rules and NAT policies

✅ **Multi-Vendor Support**
- Generate **RouterOS** configuration scripts (.rsc files)
- Generate **OpenWrt** UCI configuration files (network, wireless, firewall)

✅ **Configuration Diff**
- Compare generated configs with current router exports
- Show exactly what will change before applying
- Prevent accidental misconfigurations

✅ **Local Test Lab**
- Docker Compose topology with RouterOS CHR and OpenWrt
- Automated connectivity tests (internet access, routing, firewall)
- Guest Wi-Fi isolation verification
- VPN reachability checks

✅ **AI Copilot**
- Convert natural language to YAML policy draft
- Auto-generate test cases for lab validation
- Suggest security best practices

### Quick Start

#### Requirements

- Python 3.10 or higher
- Docker and Docker Compose (optional, for lab)
- QEMU (optional, for RouterOS CHR)

#### Installation

```bash
# Clone the repository
git clone https://github.com/ranas-mukminov/router-policy-to-config.git
cd router-policy-to-config

# Install the package
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

#### Basic Usage

**1. Create a policy (interactively)**
```bash
router-policy init --output policy.yaml
```

**2. Validate your policy**
```bash
router-policy validate policy.yaml
```

**3. Generate RouterOS configuration**
```bash
router-policy render policy.yaml --target routeros --out routeros-config.rsc
```

**4. Generate OpenWrt configuration**
```bash
router-policy render policy.yaml --target openwrt --out openwrt-configs/
```

**5. Compare with existing config**
```bash
# For RouterOS
router-policy diff policy.yaml --target routeros --current my-router-export.rsc

# For OpenWrt
router-policy diff policy.yaml --target openwrt --current /etc/config/
```

**6. AI-assisted policy generation**
```bash
echo "ISP via PPPoE on ether1, LAN 192.168.10.0/24, guest Wi-Fi on separate VLAN, WireGuard VPN for remote access" > intent.txt
router-policy ai-suggest --from-text intent.txt --out policy.yaml
```

**7. Test in lab before production**
```bash
router-policy lab-test policy.yaml
```

### Example Policy

```yaml
meta:
  name: home-office-router
  description: PPPoE WAN, main LAN, guest Wi-Fi, remote VPN
  target:
    vendor: routeros
    version: v7

wan:
  type: pppoe
  interface: ether1
  username: "PPPOE_USER_PLACEHOLDER"
  password_ref: "secret:pppoe_password"

lans:
  - name: main
    subnet: 192.168.10.0/24
    gateway: 192.168.10.1
    dhcp:
      enabled: true
      range: 192.168.10.100-192.168.10.200

  - name: guest
    subnet: 192.168.20.0/24
    gateway: 192.168.20.1
    dhcp:
      enabled: true
      range: 192.168.20.50-192.168.20.150
    isolated_from:
      - main

wifi:
  - name: main-wifi
    lan: main
    ssid: "MyHome"
    mode: ap
    security:
      encryption: wpa2-psk
      password_ref: "secret:wifi_main_password"

  - name: guest-wifi
    lan: guest
    ssid: "MyHome-Guest"
    mode: ap
    security:
      encryption: wpa2-psk
      password_ref: "secret:wifi_guest_password"
    guest: true

vpn:
  - type: wireguard
    role: server
    listen_port: 51820
    allowed_ips:
      - 10.10.10.0/24

firewall:
  rules:
    - name: allow_lan_to_internet
      from: [main]
      to: [wan]
      action: accept
    - name: block_guest_to_main
      from: [guest]
      to: [main]
      action: drop
    - name: allow_vpn_to_main
      from: [vpn]
      to: [main]
      action: accept
```

### How It Works

1. **Policy Validation** - YAML policy is validated against JSON Schema and semantic rules (no subnet overlaps, valid CIDR notation, etc.)

2. **Intermediate Model** - Policy is converted to an internal data model with vendor-agnostic representations

3. **Vendor Backend** - Target-specific backend (RouterOS or OpenWrt) generates configuration:
   - RouterOS: Generates `/system`, `/interface`, `/ip`, `/routing`, `/firewall` commands
   - OpenWrt: Generates UCI config sections for `network`, `wireless`, `firewall`, `dhcp`

4. **Diff Engine** - Compares generated configuration with current router state:
   - Normalizes both configs to canonical form
   - Computes additions, deletions, and modifications
   - Outputs human-readable change summary

5. **Lab Validation** - Before production deployment:
   - Spins up RouterOS CHR and OpenWrt in Docker/QEMU
   - Applies generated configuration
   - Runs connectivity and security tests
   - Reports pass/fail for each scenario

### Security and Limitations

#### What this tool DOES NOT do:

❌ Brute-force, scan, or exploit routers  
❌ Automatically modify remote routers (v1.0)  
❌ Store credentials or secrets in Git  
❌ Bypass ISP restrictions or policies  

#### Intended Use:

✅ Routers and networks you own or administer  
✅ Defensive and operational network management  
✅ Safe lab testing before production changes  
✅ Version-controlled infrastructure-as-code  

#### Secret Management:

- Policies use **references** (`password_ref: "secret:name"`) instead of literal secrets
- Actual secrets loaded from:
  - Environment variables (`ROUTER_SECRET_NAME`)
  - External secret providers (HashiCorp Vault, AWS Secrets Manager)
  - Encrypted secret files (not committed to Git)

### Professional Services by run-as-daemon.ru

This project is maintained by the DevSecOps / network engineer behind **[run-as-daemon.ru](https://run-as-daemon.ru)**.

If you need professional help with:

🔧 **Network Design**
- Designing RouterOS + OpenWrt networks "from policy, not CLI"
- Multi-site network architecture with VPN interconnection
- Guest network isolation and captive portals
- Enterprise-grade firewall and security policies

🔄 **Migration**
- Migrating existing routers to policy-driven configuration
- Converting manual configs to version-controlled YAML
- Consolidating multi-vendor networks

🧪 **Testing & CI/CD**
- Building safe test labs for router configuration changes
- Setting up CI pipelines for network infrastructure
- Automated validation of firewall rules and routing policies

📚 **Training & Support**
- Team training on RouterOS and OpenWrt
- Ongoing support and configuration review
- Custom policy extensions for your use cases

**Contact:** [run-as-daemon.ru](https://run-as-daemon.ru) for consulting, implementation, and ongoing support.

### Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Code style guidelines (Ruff, Black, isort)
- How to run tests (`pytest`)
- How to add new policy fields
- How to add support for new vendors
- How to extend the AI copilot

### Development Setup

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linters
./scripts/lint.sh

# Format code
./scripts/format.sh

# Security scan
./scripts/security_scan.sh

# Performance check
./scripts/perf_check.sh
```

### Architecture

```
Policy YAML
    ↓
Schema Validation (policy-schema.yaml)
    ↓
Semantic Validation (subnet overlaps, etc.)
    ↓
Internal Model (vendor-agnostic)
    ↓
    ├─→ RouterOS Backend → .rsc script
    ├─→ OpenWrt Backend → UCI files
    └─→ Future vendors...
    ↓
Diff Engine (vs current config)
    ↓
Lab Testing (optional)
    ↓
Manual Review & Apply
```

### Roadmap

- [x] Core policy validation
- [x] RouterOS backend (v6/v7)
- [x] OpenWrt backend (UCI)
- [x] Configuration diff
- [x] Local test lab
- [x] AI policy generation
- [ ] Web UI for policy editing
- [ ] VyOS support
- [ ] pfSense support
- [ ] Automated rollback on failure
- [ ] Multi-router orchestration
- [ ] Network-wide policy consistency checks

### License

Apache-2.0 - See [LICENSE](LICENSE) file for details.

### Legal

See [LEGAL.md](LEGAL.md) for important legal information about:
- Permitted use cases (own routers only)
- MikroTik and OpenWrt trademark acknowledgments
- Lab image licensing
- Security and compliance

---

## Русский (кратко)

### Что это?

**router-policy-to-config** — инструмент для генерации конфигураций роутеров из высокоуровневых YAML-политик.

Вместо ручного написания команд для MikroTik RouterOS или редактирования UCI-файлов OpenWrt, вы описываете сеть один раз и получаете:
- Скрипты RouterOS (.rsc)
- Конфигурационные файлы OpenWrt (UCI)

### Возможности

✅ **YAML-политики** - WAN (PPPoE, DHCP, статика), LAN, гостевой Wi-Fi, VPN, firewall  
✅ **Diff** - сравнение с текущей конфигурацией роутера  
✅ **Тестовая лаборатория** - Docker с RouterOS CHR и OpenWrt для безопасного тестирования  
✅ **AI-помощник** - преобразование текста в YAML-политику  

### Быстрый старт

```bash
# Установка
pip install -e .

# Создать политику
router-policy init --output policy.yaml

# Валидация
router-policy validate policy.yaml

# Сгенерировать конфигурацию RouterOS
router-policy render policy.yaml --target routeros --out routeros-config.rsc

# Сравнить с текущей конфигурацией
router-policy diff policy.yaml --target routeros --current export.rsc

# Протестировать в лаборатории
router-policy lab-test policy.yaml
```

### Пример политики

```yaml
meta:
  name: home-router
  target:
    vendor: routeros
    version: v7

wan:
  type: pppoe
  interface: ether1
  username: "user@isp.ru"
  password_ref: "secret:pppoe_password"

lans:
  - name: main
    subnet: 192.168.10.0/24
    dhcp:
      enabled: true
      range: 192.168.10.100-192.168.10.200

wifi:
  - name: main-wifi
    lan: main
    ssid: "MyHome"
    security:
      encryption: wpa2-psk
      password_ref: "secret:wifi_password"
```

### Безопасность

⚠️ **Важно:**
- Инструмент предназначен только для роутеров, которыми вы владеете
- Не выполняет автоматическое применение конфигураций (v1.0)
- Секреты хранятся в переменных окружения, не в Git
- Тестирование в локальной лаборатории перед применением в production

### Профессиональные услуги – run-as-daemon.ru

Проект поддерживается DevSecOps/сетевым инженером с сайта **[run-as-daemon.ru](https://run-as-daemon.ru)**.

Если вам нужна профессиональная помощь:

🔧 **Проектирование сети**
- Архитектура сети на основе политик, а не CLI-команд
- Мульти-сайтовые сети с VPN-связностью
- Изоляция гостевых сетей и captive-порталы

🔄 **Миграция**
- Перевод существующих роутеров на policy-driven конфигурацию
- Конвертация ручных конфигов в версионируемый YAML

🧪 **Тестирование и CI/CD**
- Создание безопасных тестовых лабораторий
- Настройка CI-пайплайнов для сетевой инфраструктуры

📚 **Обучение и поддержка**
- Обучение команд работе с RouterOS и OpenWrt
- Постоянная поддержка и ревью конфигураций

**Контакт:** [run-as-daemon.ru](https://run-as-daemon.ru) для консалтинга, внедрения и последующей поддержки.

### Лицензия

Apache-2.0 — см. файл [LICENSE](LICENSE).

### Правовая информация

См. [LEGAL.md](LEGAL.md) для важной информации о:
- Разрешённых сценариях использования (только свои роутеры)
- Товарных знаках MikroTik и OpenWrt
- Лицензировании образов для лаборатории
- Безопасности и соблюдении законов
