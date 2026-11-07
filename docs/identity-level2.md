# C4 Level 2: Container Diagram для Identity Service

Эта диаграмма показывает внутреннюю структуру Identity Service, включая основные компоненты приложения и базу данных.

```mermaid
flowchart TB
    %% Внешние акторы и системы
    customer([Покупатель])
    shop([Shop Service])

    %% Граница Identity Service (Контейнеры)
    subgraph Identity Service
        direction TB
        django["Django App<br/>(accounts, identity_core)"]
        mysql[(MySQL Database<br/>Users, OIDC Clients)]
    end

    %% Связи
    customer -- "Регистрация, Логин (HTTP)" --> django
    shop -- "GET /.well-known/jwks.json" --> django
    django -- "Чтение/Запись (SQL)" --> mysql