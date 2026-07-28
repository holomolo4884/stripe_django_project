#!/bin/sh
set -e

echo "🚀 Запуск миграций..."
python manage.py migrate --noinput

echo "📦 Сборка статики..."
python manage.py collectstatic --noinput

echo "✅ Запуск Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 stripe_django.wsgi:application