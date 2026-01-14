#!/bin/bash
set -e

./wait_for_db.sh

echo "🚀 Iniciando Celery Beat..."
exec celery -A maintenance_django beat -l INFO