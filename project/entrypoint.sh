#!/bin/sh

until cd /code
do
    echo "Waiting for server volume..."
done


until python manage.py migrate
do
    echo "Waiting for db to be ready..."
    sleep 2
done


# Allow platform to specify port and workers
PORT="${PORT:-8000}"
WORKERS="${WORKERS:-2}"

echo "Starting gunicorn on :$PORT with $WORKERS workers"
gunicorn --bind ":${PORT}" --workers "${WORKERS}" project.wsgi
