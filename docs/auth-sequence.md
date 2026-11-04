sequenceDiagram
    title Процесс валидации JWT токена в Shop Service

    participant Customer as Покупатель
    participant Shop as Shop Service
    participant Cache as JWKS Кэш
    participant Identity as Identity Service

    Customer->>Shop: HTTP запрос с JWT токеном в заголовке
    Shop->>Shop: Извлечь токен из заголовка Authorization
    Shop->>Cache: Проверить наличие ключа в кэше
   
    alt Кэш пуст или ключ устарел
        Cache-->>Shop: Ключ не найден
        Shop->>Identity: GET /.well-known/jwks.json (Запросить публичные ключи)
        Identity-->>Shop: Вернуть набор JWKS ключей
        Shop->>Cache: Сохранить новые ключи в кэш
    else Кэш содержит актуальный ключ
        Cache-->>Shop: Вернуть публичный ключ
    end

    Shop->>Shop: Математически проверить подпись токена с помощью ключа

    alt Подпись валидна и токен не просрочен
        Shop->>Customer: 200 OK (успешный ответ с данными)
    else Подпись невалидна или токен просрочен
        Shop->>Customer: 401 Unauthorized (ошибка аутентификации)
    end