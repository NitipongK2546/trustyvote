#!/bin/bash

# Wait for the database to be ready
echo "Waiting for MariaDB..."

while ! nc -z $DB_HOST 3306; do
  sleep 1
done

echo "MariaDB is up!"

# Run migrations
python manage.py migrate --noinput

RUN python manage.py collectstatic --noinput

# Start Django server
gunicorn trustyvote.wsgi:application --bind 0.0.0.0:8000