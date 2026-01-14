#!/bin/bash
set -e

./wait_for_db.sh

echo "🚀 Iniciando Celery Worker..."
exec celery -A maintenance_django worker -l INFO
