# Django Ecommerce 
Интернет‑магазин на Django с REST API, JWT‑аутентификацией, документацией по OpenAPI и готовым к деплою окружением.



## Особенности проекта
- REST API на Django REST Framework с полной документацией по OpenAPI (Swagger/ReDoc)
- JWT‑аутентификация (access + refresh токены)
- Кастомная модель пользователя и система прав
-  Unit‑тесты с покрытием логики и mocking'ом
- Docker‑контейнеризация (Dockerfile + docker‑compose.yml)
-  CI/CD через GitHub Actions с автоматическим прогоном тестов
- - **Payment Domain с учётом промышленных практик:**
- ACID‑транзакции (`transaction.atomic`)
- Защита от race conditions (`select_for_update`)
-  Идемпотентность операций через UUID‑ключи


## Установка и запуск
1.Клонируйте репозиторий:
git clone https://github.com/vagram-dl/django-ecommerce.git
cd   django-ecommerce
2.Создайте виртуальное окружение и активируйте его:
python -m venv .venv
source .venv/bin/activate #Linux
.venv\Scripts\activate #Windows
3.Установите зависимости 
pip install -r requirements.txt
4.Примените миграции
python manage.py migrate
5.Запустите сервер разработки
python manage.py runserver

## Документация API
- [http://127.0.0.1:8000/](http://127.0.0.1:8000/) — главная страница
- [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/)
-  [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
-  [http://127.0.0.1:8000/api/redoc/](http://127.0.0.1:8000/api/redoc/)

## Деплой на VPS (Ubuntu) 
- Установить Python, pip, virtualenv
- Установить MySQL и создать базу
- Клонировать проект и установить зависимости
- Применить миграции и собрать статику
- Запустить через Gunicorn: gunicorn myproject.wsgi:application
- Настроить Nginx для отдачи статики из папки staticfiles

## Запуск через Docker
docker-compose up --build

## Тестирование
python manage.py test

## Деплой на VPS(Ubuntu)
1.Установите Python,pip и virtualenv:
sudo apt update && sudo apt install python3 python3-pip python3-venv

2.Установите MySQL и создайте базу данных.

3.Клонируйте проект и установите зависимости:
git clone https://github.com/vagram-dl/django-ecommerce.git
cd django-ecommerce
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirments.txt

4.Примените миграции и соберите статику:
python manage.py migrate
python manage.py collectstatic

5.Запустите через Gunicorn:
gunicorn shop_project.wsgi:application

6.Настройте Nginx для отдачи статики из папки staticfiles.

Используемый стек
- Python 3.12
- Django 6
- Django REST Framework
- JWT (djangorestframework-simplejwt)
- MySQL
- Docker & Docker Compose
- GitHub Actions (CI/CD)
- Gunicorn + Nginx