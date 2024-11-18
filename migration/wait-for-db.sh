#!/bin/sh

TIMEOUT=60
COUNTER=0

echo "Waiting for PostgreSQL to be ready..."
until pg_isready -h $DB_HOST -p 5432 -U $DB_USER; do
  sleep 2
  COUNTER=$((COUNTER+2))
  if [ $COUNTER -ge $TIMEOUT ]; then
    echo "PostgreSQL is not ready after $TIMEOUT seconds."
    exit 1
  fi
done

echo "PostgreSQL is ready, running migrations..."

cd migration
goose postgres "postgres://$DB_USER:$DB_PASSWORD@$DB_HOST:5432/sporting?sslmode=disable" up

