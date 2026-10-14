import requests
import jwt

IDENTITY_URL = "http://localhost:8000/api/auth/login/"
SHOP_URL = "http://localhost:8001/api/test-auth/"

USER_DATA = {
    "password":"admin123",
    "email" : "admin@test.com"
}

print("Шаг 1: Получаем токен от identity-service...")
try:
    response_login = requests.post(IDENTITY_URL, json=USER_DATA, timeout=5)

    if response_login.status_code != 200:
        print(f"Ошибка логина: {response_login.status_code}")
        print(f"Ответ сервера: {response_login.text}")
    else:
        response_login.raise_for_status()
        token_data = response_login.json()

        token = token_data.get('id_token') or token_data.get('access')

        print(f"Токен получен! (Длина: {len(token)} симв.)\n")

        header = jwt.get_unverified_header(token)
        print(f"Заголовок токена: {header}\n")

        print("Шаг 2: Проверяем токен в shop-service...")
        headers = {"Authorization": f"Bearer {token}"}

        response_shop = requests.get(SHOP_URL, headers=headers, timeout=5)

        print(f"Статус от shop-service: {response_shop.status_code}")
        print(f"Ответ: {response_shop.text}")

        if response_shop.status_code == 200:
            print("\nУСПЕХ! Связка работает, JWKS-кэш проверил токен!")
        else:
            print("\nЧто-то пошло не так. Проверь логи shop-service.")

except requests.exceptions.RequestException as e:
    print(f"Ошибка сети: {e}")
