#!/bin/bash
set -e

./wait_for_db.sh

echo "🕒 Aplicando migrations..."
python3 manage.py migrate --noinput

echo "👤 Criando superuser (se não existir)..."
python3 manage.py shell <<EOF
from django.contrib.auth.models import User
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser(
        "admin",
        "admin@test.com",
        "admin"
    )
EOF

echo "🚀 Iniciando Django..."
exec python3 manage.py runserver 0.0.0.0:8000
