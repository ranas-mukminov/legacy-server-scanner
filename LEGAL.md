# LEGAL / Правовое уведомление

## English

### Permitted Use

**router-policy-to-config** and the **legacy-migration-assistant** tools are designed for legitimate network administration and infrastructure management.

**You MAY use these tools:**
- On routers and networks you own or administer with explicit authorization
- For defensive security, operational management, and infrastructure-as-code
- To test configurations in isolated lab environments before production deployment
- For educational and research purposes in controlled environments

**You MUST NOT use these tools to:**
- Access, modify, or scan routers or networks without explicit authorization
- Attack, exploit, or take over third-party systems
- Bypass ISP restrictions, security controls, or access controls
- Store or distribute credentials, secrets, or sensitive configuration data
- Violate any applicable laws, regulations, or terms of service

### Trademarks and Third-Party Rights

- **MikroTik** and **RouterOS** are trademarks of SIA Mikrotīkls (MikroTik). This project is not affiliated with, endorsed by, or sponsored by MikroTik.
- **OpenWrt** is an open-source project with its own licensing terms. This project respects and complies with OpenWrt's GPL and related licenses.
- All vendor-specific syntax and commands are used for legitimate configuration generation purposes under fair use principles.

### Lab Images and Testing

- Lab Docker/QEMU images are intended **for testing purposes only**
- Do not use lab images or configurations in production environments
- RouterOS CHR (Cloud Hosted Router) images must comply with MikroTik's licensing terms
- Users are responsible for obtaining proper licenses for any commercial use

### Secrets and Sensitive Data

- Never commit secrets, passwords, or credentials to version control
- Use secret references (`secret:name`) in policy files
- Actual secrets must be stored in environment variables or external secret managers
- You are responsible for protecting sensitive configuration data

### AI and External Services

- When using AI features, you are responsible for data shared with AI providers
- Anonymize or redact sensitive information before using AI assistance
- Review and validate all AI-generated configurations before deployment
- The project authors are not responsible for AI-generated content accuracy

### Disclaimer

This software is provided "AS IS" without warranty of any kind, express or implied. The authors and contributors:
- Are not liable for any damages arising from use or misuse of this software
- Do not guarantee that generated configurations are secure or correct
- Strongly recommend thorough review and testing before production deployment
- Are not responsible for network outages, security incidents, or data loss

**Always review, test, and validate configurations in a safe environment before applying to production systems.**

### License

This project is licensed under the Apache License 2.0. See the LICENSE file for full terms.

---

## Русский (основное)

### Разрешённое использование

**router-policy-to-config** и **legacy-migration-assistant** предназначены для легального администрирования сетей и инфраструктуры.

**Вы МОЖЕТЕ использовать эти инструменты:**
- На роутерах и сетях, которыми владеете или администрируете на законных основаниях
- Для защиты, операционного управления и infrastructure-as-code
- Для тестирования конфигураций в изолированных лабораторных средах
- В образовательных и исследовательских целях в контролируемых условиях

**Вы НЕ ДОЛЖНЫ использовать эти инструменты для:**
- Доступа, изменения или сканирования чужих роутеров без явного разрешения
- Атак, эксплуатации или захвата сторонних систем
- Обхода ограничений провайдера, средств защиты или контроля доступа
- Хранения или распространения учётных данных, секретов или конфиденциальных конфигураций
- Нарушения законов, правил или условий обслуживания

### Товарные знаки и права третьих лиц

- **MikroTik** и **RouterOS** являются товарными знаками SIA Mikrotīkls (MikroTik). Этот проект не связан с MikroTik и не одобрен ими.
- **OpenWrt** — проект с открытым исходным кодом со своими условиями лицензирования. Проект соблюдает GPL OpenWrt и связанные лицензии.

### Лабораторные образы и тестирование

- Лабораторные Docker/QEMU-образы предназначены **только для тестирования**
- Не используйте лабораторные образы или конфигурации в production
- Образы RouterOS CHR должны соответствовать условиям лицензирования MikroTik
- Пользователи несут ответственность за получение надлежащих лицензий для коммерческого использования

### Секреты и конфиденциальные данные

- Никогда не сохраняйте секреты, пароли или учётные данные в системе контроля версий
- Используйте ссылки на секреты (`secret:name`) в файлах политик
- Фактические секреты должны храниться в переменных окружения или внешних менеджерах секретов
- Вы отвечаете за защиту конфиденциальных данных конфигурации

### Отказ от ответственности

Программное обеспечение предоставляется «КАК ЕСТЬ» без каких-либо гарантий. Авторы и участники:
- Не несут ответственности за ущерб от использования или неправильного использования
- Не гарантируют, что сгенерированные конфигурации безопасны или корректны
- Настоятельно рекомендуют тщательный аудит и тестирование перед развёртыванием
- Не отвечают за сбои сети, инциденты безопасности или потерю данных

**Всегда проверяйте, тестируйте и валидируйте конфигурации в безопасной среде перед применением в production.**

### Лицензия

Проект лицензирован под Apache License 2.0. См. файл LICENSE.
