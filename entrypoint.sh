#!/bin/sh
set -e

echo "🔄 Running migrations..."
python manage.py migrate --noinput

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo "👤 Creating superuser..."
python manage.py createsuperuser --noinput --username admin --email admin@example.com 2>/dev/null || true

echo "🚀 Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 stripe_django.wsgi:application