#!/bin/bash
set -e

./wait_for_db.sh

echo "🧹 Resetando migrations do Celery Beat..."
# Volta todas as migrations do django_celery_beat
python3 manage.py migrate django_celery_beat zero --noinput

# Aplica novamente todas as migrations do django_celery_beat
python3 manage.py migrate django_celery_beat --noinput

echo "🚀 Iniciando Celery Beat..."
exec celery -A maintenance_django beat -l INFO
