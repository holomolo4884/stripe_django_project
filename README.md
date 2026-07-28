# Stripe Django Demo

Django приложение с интеграцией платежной системы Stripe.

## Демо

Приложение доступно по адресу: [https://stripe-django-app.onrender.com](https://stripe-django-app.onrender.com)

**Админ-панель:**
- URL: [https://stripe-django-app.onrender.com/admin](https://stripe-django-app.onrender.com/admin)
- Логин: `admin`
- Пароль: `admin123`

## Запуск

### Локальный запуск (без Docker)

```bash
# 1. Клонировать репозиторий
git clone https://github.com/holomolo4884/stripe_django_project.git
cd stripe_django_project

# 2. Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate на Windows

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Создать .env файл
cp .env.example .env
# Отредактировать .env и добавить Stripe ключи

# 5. Применить миграции
python manage.py migrate

# 6. Создать суперпользователя
python manage.py createsuperuser

# 7. Запустить сервер
python manage.py runserver 8000
```

После запуска приложение будет доступно по адресу: http://localhost:8000

### Запуск через Docker

```bash
# 1. Клонировать репозиторий
git clone https://github.com/holomolo4884/stripe_django_project.git
cd stripe_django_project

# 2. Создать .env файл
cp .env.example .env
# Отредактировать .env и добавить Stripe ключи

# 3. Запустить через Docker Compose
docker-compose up --build
```

После запуска приложение будет доступно по адресу: http://localhost:8000

## ⚙️ Переменные окружения (.env)

```env
# Django
SECRET_KEY=django-insecure-your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (для Docker)
DATABASE_NAME=stripe_user
DATABASE_USER=stripe_user
DATABASE_PASSWORD=123
DATABASE_HOST=db
DATABASE_PORT=5432

# Stripe USD
STRIPE_PUBLISHABLE_KEY_USD=pk_test_xxx
STRIPE_SECRET_KEY_USD=sk_test_xxx

# Stripe EUR
STRIPE_PUBLISHABLE_KEY_EUR=pk_test_xxx
STRIPE_SECRET_KEY_EUR=sk_test_xxx
```

## 🧪 Тестирование платежей

**Тестовая карта Stripe:**
- Номер: `4242 4242 4242 4242`
- Дата: любая будущая
- CVC: любые 3 цифры
