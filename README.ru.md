# Legacy Migration Assistant

## Обзор
Legacy Migration Assistant помогает инвентаризировать легаси Linux-серверы, построить карту приложения, а затем подготовить черновые артефакты контейнеризации: `docker-compose.yml` и Kubernetes-манифесты. Инструмент рассчитан на легальное использование администраторами и владельцами инфраструктуры.

## Возможности
- Сканирование пакетов, сервисов systemd/init, открытых портов, cron, конфигов web/db/cache/queue.
- Построение application map: компоненты (web, db, cache, queue, cron, infra) и связи между ними.
- Генерация чернового `docker-compose.yml` с volumes, портами, depends_on и комментариями TODO.
- Конвертация compose или карты в K8s-манифесты (Deployment/StatefulSet, Service, Ingress, ConfigMap, Secret) с базовыми security-настройками, probes и ресурсами.
- AI-слой (опционально) для подсказок по классификации, ресурсам и аннотациям.

## Быстрый старт
На легаси-сервере (с правами администратора):
```bash
pip install legacy-migration-assistant
legacy-scan scan --output scan.json
legacy-scan map --scan scan.json --output app-map.yaml
legacy-scan compose --map app-map.yaml --output docker-compose.yaml
```
На рабочей станции:
```bash
legacy-k8s from-compose --compose docker-compose.yaml --output-dir k8s/
```
Перед применением ревьюйте YAML и вычищайте секреты.

## Архитектура репозитория
- `legacy_server_scanner` — сбор данных, классификация и генерация compose.
- `legacy_to_k8s_blueprints` — генерация Kubernetes шаблонов из compose или карты.
- `ai` — интерфейсы и Noop-провайдер для текстовых подсказок.
- `examples/` — примеры карт, compose и K8s-манифестов.
- `scripts/` — линтинг, безопасность, перфоманс.

## Безопасность и правовая часть
- Используйте на серверах, к которым у вас есть законный доступ.
- Не выгружайте пароли/секреты в отчеты и ИИ. Инструмент не читает содержимое ключей.
- Все сгенерированные манифесты требуют ручного аудита перед продом.

## Участие
PR и issue приветствуются. См. `CONTRIBUTING.md`.

## Лицензия
Apache-2.0, см. `LICENSE`.
