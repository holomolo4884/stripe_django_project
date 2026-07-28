#!/bin/sh
set -e

echo "🔄 Running migrations..."
python manage.py migrate --noinput

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo "👤 Creating superuser with password admin123..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if User.objects.filter(username='admin').exists():
    user = User.objects.get(username='admin')
    user.set_password('admin123')
    user.save()
    print("✅ Password reset to admin123")
else:
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("✅ Superuser created with password admin123")
EOF

echo "🚀 Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 stripe_django.wsgi:application