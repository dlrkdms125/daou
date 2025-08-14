
#!/usr/bin/env bash
set -e
python manage.py migrate --noinput || true
celery -A eschecker beat -l info
