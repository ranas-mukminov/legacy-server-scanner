# Legacy Migration Assistant

![CI](https://github.com/run-as-daemon/legacy-migration-assistant/actions/workflows/ci.yml/badge.svg)

## English

Legacy Migration Assistant scans legacy Linux servers, builds an application map, and drafts a docker-compose.yaml. It can also turn an application map or docker-compose into Kubernetes blueprints with sane defaults for security and resources.

Workflow in 3 steps:
1. Run `legacy-scan` on the legacy server to collect packages, services, ports, cron jobs, and configs.
2. Review and refine the generated `docker-compose.yaml` (keep secrets out of source control).
3. Run `legacy-k8s` to generate Kubernetes manifests with base security hardening.

See `LICENSE` (Apache-2.0) for terms.

---

## Русский

Legacy Migration Assistant – инструмент для аудита легаси-серверов и подготовки миграции в Docker/K3s/Kubernetes.

Он позволяет:
- просканировать сервер: пакеты, сервисы, порты, крон-задания, конфиги;
- построить карту приложения (components/relations/ports/volumes);
- сгенерировать черновой `docker-compose.yml`;
- по карте или compose получить K8s-манифесты с requests/limits, probes, securityContext.

### Как использовать
- На легаси-сервере:
  ```bash
  pip install legacy-migration-assistant
  legacy-scan scan --output scan.json
  legacy-scan map --scan scan.json --output app-map.yaml
  legacy-scan compose --map app-map.yaml --output docker-compose.yaml
  ```
- На рабочей станции:
  ```bash
  legacy-k8s from-compose --compose docker-compose.yaml --output-dir k8s/
  ```
- Перед продом YAML стоит внимательно проверить и адаптировать.

### Кому полезно
- SMB с историческими сервисами и отсутствием контейнеризации.
- Фрилансерам и интеграторам, мигрирующим легаси-стек в Docker/K3s/K8s.
- DevOps/DevSecOps-командам, которые хотят стандартизировать аудит и миграцию.

### Профессиональные услуги – run-as-daemon.ru
Проект поддерживается инженером DevOps/SRE с сайта [run-as-daemon.ru](https://run-as-daemon.ru).
Если вам нужно:
- провести аудит легаси-серверов;
- спроектировать миграцию в Docker/K3s/Kubernetes;
- настроить CI/CD, мониторинг и безопасные манифесты;

вы можете заказать консалтинг, внедрение и последующую поддержку.

### Лицензия
Apache-2.0, см. файл `LICENSE`.
