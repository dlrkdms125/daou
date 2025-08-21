import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "dev-secret-key"
DEBUG = os.environ.get("DJANGO_DEBUG", "0") == "1"
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "checks",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "eschecker.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "eschecker.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.getenv("DB_HOST", "db"),
        "PORT": os.getenv("DB_PORT", "5432"),
        "NAME": os.getenv("DB_NAME", "eschecker"),
        "USER": os.getenv("DB_USER", "kaeunlee"),
        "PASSWORD": os.getenv("DB_PASSWORD", "qwer1234"),
    }
}

LANGUAGE_CODE = "ko-kr"
TIME_ZONE = os.environ.get("TZ", "Asia/Seoul")
USE_I18N = True
USE_TZ = False

# ---- Static files ----
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# WhiteNoise는 SecurityMiddleware 바로 뒤에 이미 추가되어 있음
# 배포 시 collectstatic 필요:
#   python manage.py collectstatic
# 옵션: 압축/매니페스트 스토리지 사용하려면 아래 주석 해제
# STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ---- Elasticsearch ----
ES_HOST = os.environ.get("ES_HOST", "http://localhost:9200")
ES_INDEX = os.environ.get("ES_INDEX", "check*")
DEMO_MODE = os.environ.get("DEMO_MODE", "false").lower() == "true"

# ---- 스케줄러(선택) ----
SCHEDULER_ENABLED = os.environ.get("SCHEDULER_ENABLED", "true").lower() == "true"
FETCH_INTERVAL_SECONDS = int(os.environ.get("FETCH_INTERVAL_SECONDS", "60"))
