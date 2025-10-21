
#!/usr/bin/env bash
set -e
python manage.py migrate --noinput
python manage.py collectstatic --noinput
exec python manage.py runserver 0.0.0.0:8000 --noreload --insecure # 개발 서버 reloader가 켜져 있으면 스케줄러가 비정상일 수 있음



