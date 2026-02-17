import os
import secrets
from pathlib import Path

# BASE DIR
BASE_DIR = Path(__file__).resolve().parent.parent

# ENV
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# =============================
# SEGURIDAD
# =============================

# Use SECRET_KEY from environment, otherwise generate a long dev key
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(50))

# DEBUG mode based on environment
DEBUG = True

# ALLOWED_HOSTS default for local dev; override via env var in prod
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# CSRF TRUSTED ORIGINS for browser preview and development
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

# Additional CSRF settings for development
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = None  # Allow cross-site requests for development
CSRF_COOKIE_DOMAIN = None  # Allow any domain for development

# CORS settings for development
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "http://127.0.0.1:52352,http://localhost:52352,http://127.0.0.1:8000,http://localhost:8000,http://127.0.0.1:61415,http://localhost:61415").split(",")
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = DEBUG  # Allow all origins in development
CORS_ALLOW_ALL_HEADERS = True  # Allow all headers for development
CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]

# Security settings: strict for production, relaxed for development
if ENVIRONMENT == "production":
    SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "31536000"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv("SECURE_HSTS_INCLUDE_SUBDOMAINS", "True") == "True"
    SECURE_HSTS_PRELOAD = os.getenv("SECURE_HSTS_PRELOAD", "True") == "True"
    SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "True") == "True"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "True") == "True"
    CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "True") == "True"
else:
    # Development: disable SSL/TLS requirements for local testing
    SECURE_SSL_REDIRECT = False
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# Session settings for development
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = None
SESSION_COOKIE_DOMAIN = None

# =============================
# TEMPLATES
# =============================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "plataforma/templates"],
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

# Sites Framework
SITE_ID = 1

# Allauth Configuration
AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
    # Social auth
    # Backends provided by python-social-auth / social-auth-app-django
    "social_core.backends.google.GoogleOAuth2",
    "social_core.backends.microsoft.MicrosoftOAuth2",
]

# Allauth settings (updated to new format)
ACCOUNT_LOGIN_METHODS = {"username", "email"}
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_LOGIN_REDIRECT_URL = "/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"
ACCOUNT_CONFIRMATION_EMAIL_REQUIRED = False

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
    },
    "microsoft": {
        "SCOPE": [
            "User.Read",
        ],
        "TENANT": "common",
    },
}

# =============================
# EMAIL CONFIGURATION
# =============================

# Configuración para desarrollo (Console Backend)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Para Gmail (actualizar con credenciales reales)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'tu-email@gmail.com'
# EMAIL_HOST_PASSWORD = 'tu-app-password'
# DEFAULT_FROM_EMAIL = 'tu-email@gmail.com'

# =============================
# CELERY CONFIGURATION
# =============================

CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "America/Bogota"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutos

# =============================
# APLICACIONES
# =============================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # Third-party apps
    "rest_framework",
    "corsheaders",
    "drf_spectacular",
    "channels",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.microsoft",
    # Python Social Auth integration
    "social_django",
    "django_celery_beat",
    # Local apps
    "plataforma",
]

# =============================
# MIDDLEWARE
# =============================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "plataforma.middleware.FuncionarioOnlyMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

# =============================
# URLS / WSGI
# =============================

ROOT_URLCONF = "sgva.urls"

WSGI_APPLICATION = "sgva.wsgi.application"

# =============================
# BASE DE DATOS
# =============================

DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.getenv("DB_NAME", str(BASE_DIR / "db.sqlite3")),
    }
}

if os.getenv("DB_USER"):
    DATABASES["default"]["USER"] = os.getenv("DB_USER")
if os.getenv("DB_PASSWORD"):
    DATABASES["default"]["PASSWORD"] = os.getenv("DB_PASSWORD")
if os.getenv("DB_HOST"):
    DATABASES["default"]["HOST"] = os.getenv("DB_HOST")
if os.getenv("DB_PORT"):
    DATABASES["default"]["PORT"] = os.getenv("DB_PORT")

# =============================
# PASSWORDS
# =============================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": ("django.contrib.auth.password_validation." "MinimumLengthValidator"),
    },
    {
        "NAME": ("django.contrib.auth.password_validation." "CommonPasswordValidator"),
    },
    {
        "NAME": ("django.contrib.auth.password_validation." "NumericPasswordValidator"),
    },
]

# =============================
# INTERNACIONALIZACIÓN
# =============================

LANGUAGE_CODE = "es-co"

TIME_ZONE = "America/Bogota"

USE_I18N = True

USE_TZ = True

# =============================
# CONFIGURACIÓN DE AUTENTICACIÓN
# =============================

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "inicio"

# =============================
# ARCHIVOS ESTÁTICOS
# =============================

STATIC_URL = "static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"

# =============================
# CLAVE PRIMARIA
# =============================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =============================
# REST FRAMEWORK
# =============================

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": ("rest_framework.pagination.PageNumberPagination"),
    "PAGE_SIZE": 25,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# =============================
# SPECTACULAR (Swagger/OpenAPI)
# =============================

SPECTACULAR_SETTINGS = {
    "TITLE": "SGVA API",
    "DESCRIPTION": ("API REST para Sistema de Gestión de Vinculación " "de Aprendices"),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# =============================
# CORS (Permitir acceso desde el frontend)
# =============================

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True

# =============================
# CHANNELS
# =============================

ASGI_APPLICATION = "sgva.asgi.application"

CHANNEL_LAYERS = [
    {
        "BACKEND": "channels.security.WebSocketDenier",
    },
    {
        "BACKEND": "channels.auth.AuthMiddlewareStack",
        "MIDDLEWARE": [
            "corsheaders.middleware.CorsMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "channels.middleware.ChannelLayerMiddleware",
        ],
    },
]

# =============================
# CELERY BEAT CONFIGURATION
# =============================

CELERY_BEAT_SCHEDULE = {
    "actualizar-estadisticas": {
        "task": "plataforma.tasks.actualizar_estadisticas_diarias",
        "schedule": {
            "minute": "0",
            "hour": "*/1"
        },  # Cada hora
    },
}
