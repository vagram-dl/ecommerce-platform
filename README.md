# E-commerce Platform

E-commerce platform evolving from a modular monolith to a microservices architecture. Features Django, custom OIDC provider, and event-driven communication (Kafka).

## Архитектура и сервисы

Проект состоит из независимых микросервисов:
- **`identity-service`** (порт 8000): Отвечает за аутентификацию, регистрацию пользователей и выдачу JWT-токенов (OIDC Provider). Реализует endpoint `/.well-known/jwks.json` для предоставления публичных ключей.
- **`shop-service`** (порт 8001): Основной сервис магазина. Проверяет входящие JWT-токены асинхронно, забирая публичные ключи из `identity-service` через потокобезопасный JWKS-кэш с TTL и механизмом Graceful Degradation.

## Быстрый старт

Для локальной разработки требуется Python 3.12+ и активированные виртуальные окружения.

1. **Запуск Identity Service:**
   ```bash
   cd services/identity-service
   source venv/bin/activate  # или venv\Scripts\activate на Windows
   python manage.py runserver 8000