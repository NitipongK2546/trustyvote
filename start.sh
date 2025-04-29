#!/bin/bash

# Wait for the database to be ready
echo "Waiting for MariaDB..."

while ! nc -z $DB_HOST 3306; do
  sleep 1
done

echo "MariaDB is up!"

# Run migrations
python manage.py migrate --noinput

# Start Django server
python manage.py runserver 0.0.0.0:8000
