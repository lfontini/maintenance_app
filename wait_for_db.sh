#!/bin/bash
set -e

echo "⏳ Aguardando Postgres em $POSTGRES_HOST:$POSTGRES_PORT..."

while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 1
done

echo "✅ Postgres disponível!"
