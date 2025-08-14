
#!/usr/bin/env bash
set -e
python manage.py migrate --noinput || true
celery -A eschecker worker -l info
