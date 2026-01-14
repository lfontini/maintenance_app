#!/bin/bash
set -e

./scripts/wait_for_db.sh

echo "🕒 Aplicando migrations do django_celery_beat..."
python3 manage.py migrate django_celery_beat --noinput

echo "🚀 Iniciando Celery Beat..."
exec celery -A maintenance_django beat -l INFO
