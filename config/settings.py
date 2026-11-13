"""
Django settings for RUDRAM disaster management platform.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-rudram-smart-india-hackathon-2026-disaster-resilience")
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")
SITE_URL = os.getenv("SITE_URL", "").strip().rstrip("/")
PUBLIC_ORGANIZATION_EMAIL = os.getenv("PUBLIC_ORGANIZATION_EMAIL", "ratikantaas512@gmail.com").strip()
PUBLIC_ORGANIZATION_PHONE = os.getenv("PUBLIC_ORGANIZATION_PHONE", "9078835620").strip()

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'corsheaders',
    'django_filters',

    # RUDRAM Core & Domain Apps
    'apps.core',
    'apps.accounts',
    'apps.disasters',
    'apps.risk',
    'apps.weather',
    'apps.population',
    'apps.infrastructure',
    'apps.shelters',
    'apps.resources',
    'apps.evacuation',
    'apps.assistant',
    'apps.satellite',
    'apps.alerts',
    'apps.reports',
    'apps.fire',
    'demo',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.rudram_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Database Setup
# Primary: MySQL 8.x
# Fallback: SQLite for seamless zero-dependency local development if MySQL host is unreachable
db_engine = os.getenv("DB_ENGINE", "django.db.backends.mysql")
db_name = os.getenv("DB_NAME", "rudram_db")
db_user = os.getenv("DB_USER", "rudram_user")
db_password = os.getenv("DB_PASSWORD", "secure-development-password")
db_host = os.getenv("DB_HOST", "127.0.0.1")
db_port = os.getenv("DB_PORT", "3306")
db_fallback = os.getenv("DB_FALLBACK_SQLITE", "True").lower() in ("true", "1", "t")

mysql_config = {
    'ENGINE': db_engine,
    'NAME': db_name,
    'USER': db_user,
    'PASSWORD': db_password,
    'HOST': db_host,
    'PORT': db_port,
    'OPTIONS': {
        'charset': 'utf8mb4',
        'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
    }
}

sqlite_config = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': BASE_DIR / 'db.sqlite3',
}

# Test connection to MySQL if configured, else fallback if allowed
def test_mysql_connection():
    try:
        import pymysql
        conn = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            port=int(db_port),
            connect_timeout=2
        )
        conn.close()
        return True
    except Exception:
        return False

if 'test' in sys.argv or 'pytest' in sys.argv[0]:
    DATABASES = {'default': sqlite_config}
elif db_engine == "django.db.backends.mysql" and db_fallback:
    if test_mysql_connection():
        DATABASES = {'default': mysql_config}
    else:
        print("[RUDRAM NOTICE] Local MySQL service not detected. Using SQLite for local development. For Docker/Production, MySQL 8 will be used automatically.")
        DATABASES = {'default': sqlite_config}
else:
    DATABASES = {'default': mysql_config}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = True

# Mode and External Services
DEMO_MODE = os.getenv("DEMO_MODE", "False").lower() in ("true", "1", "t")

OPEN_METEO_URL = os.getenv("OPEN_METEO_URL", "https://api.open-meteo.com")
NASA_POWER_URL = os.getenv("NASA_POWER_URL", "https://power.larc.nasa.gov")
OVERPASS_URL = os.getenv("OVERPASS_URL", "https://overpass-api.de/api/interpreter")
OSRM_URL = os.getenv("OSRM_URL", "https://router.project-osrm.org")

GEE_ENABLED = os.getenv("GEE_ENABLED", "True").lower() in ("true", "1", "t")
GEE_PROJECT_ID = os.getenv("GEE_PROJECT_ID", "rudram-disaster-intelligence")
GEE_SERVICE_ACCOUNT = os.getenv("GEE_SERVICE_ACCOUNT", "rudram-earth-engine@rudram-disaster-intelligence.iam.gserviceaccount.com")
GEE_PRIVATE_KEY_PATH = os.getenv("GEE_PRIVATE_KEY_PATH", "")
GEE_PRIVATE_KEY = os.getenv("GEE_PRIVATE_KEY", "")

FIRMS_API_KEY = os.getenv("FIRMS_API_KEY", "")
GPM_ENABLED = os.getenv("GPM_ENABLED", "True").lower() in ("true", "1", "t")
GPM_EARTHDATA_USERNAME = os.getenv("GPM_EARTHDATA_USERNAME", "")
GPM_EARTHDATA_PASSWORD = os.getenv("GPM_EARTHDATA_PASSWORD", "")
GPM_DATA_SOURCE = os.getenv("GPM_DATA_SOURCE", "IMERG_EARLY")
GPM_API_KEY = os.getenv("GPM_API_KEY", "")
AI_API_KEY = os.getenv("AI_API_KEY", "")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", os.getenv("AI_API_KEY", ""))
CARTO_BASEMAP_API_KEY = os.getenv("CARTO_BASEMAP_API_KEY", "").strip().strip('"').strip("'").strip()
MODEL_PATH = os.getenv("MODEL_PATH", "")

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} [{name}:{lineno}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'rudram': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Authentication Settings
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'
