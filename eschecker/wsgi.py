
import os
from django.core.wsgi import get_wsgi_application

# wsgi.py는 장고가 실행될 때 WSGI 서버가 앱을 인식할 수 있게 해줌
# 서버가 장고를 실행할 수 있게 해줌
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eschecker.settings')
application = get_wsgi_application()
