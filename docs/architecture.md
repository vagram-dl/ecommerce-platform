# Архитектура E-commerce Platform (C4 Level 1: System Context)

Эта диаграмма описывает высокоуровневый контекст системы: основных пользователей, микросервисы и их взаимодействие.

```mermaid
flowchart TB    
    %% Акторы
    customer([Покупатель])
    admin([Администратор])

    %% Система
    subgraph E-commerce Platform
        identity[Identity Service<br/>Auth & JWT Tokens]
        shop[Shop Service<br/>Catalog, Cart, Orders]
    end

    %% Связи с подписями
    customer -- "Регистрация, Логин" --> identity
    customer -- "Просмотр товаров, Заказы" --> shop
    admin -- "Управление каталогом" --> shop
    shop -- "Валидация JWT, Синхронизация профилей" --> identity