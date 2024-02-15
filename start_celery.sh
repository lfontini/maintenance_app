#!/bin/bash

# Iniciar o Celery Beat em segundo plano
celery -A maintenance_django beat -l INFO &

# Iniciar o Celery Worker
celery -A maintenance_django worker --loglevel=info
