
#!/usr/bin/env bash
set -e
python manage.py makemigrations checks --noinput || true
python manage.py migrate --noinput
python manage.py collectstatic --noinput || true
python manage.py runserver 0.0.0.0:8000
