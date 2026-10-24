
from pathlib import Path
import os
import sys

from django.contrib.messages import constants as message_constants
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse_lazy
from dotenv import load_dotenv

# Protección de Datos: las claves se leen desde el archivo .env (ver .env.example)
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

APPS_DIR = BASE_DIR / "apps"
sys.path.append(str(APPS_DIR))


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ImproperlyConfigured(
        "Falta SECRET_KEY. Copia .env.example como .env y define una clave secreta."
    )

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv(
        "ALLOWED_HOSTS", "proyectotitulo.azurewebsites.net,127.0.0.1,localhost"
    ).split(",")
    if h.strip()
]


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rangefilter',
    'usuarios',
    'productos',
    'home',
    'venta',
    'carrito',
    'django_recaptcha',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = '_config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'carrito.context_processor.total_carrito',
            ],
        },
    },
]

WSGI_APPLICATION = '_config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'es'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
# Carpeta donde `collectstatic` reúne los estáticos al desplegar en el servidor (MR-111)
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = reverse_lazy("Home:login")
LOGIN_REDIRECT_URL = reverse_lazy("Home:home")

# Los mensajes de Django usan las clases de alerta de Bootstrap
MESSAGE_TAGS = {
    message_constants.ERROR: "danger",
}

# Correo
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_TIMEOUT = 10

# Claves Correo
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
# Remitente de los correos del sitio (MR-112): siempre la cuenta de la tienda,
# nunca el correo que escribe el cliente.
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL") or EMAIL_HOST_USER or "webmaster@localhost"
# Correo que recibe las solicitudes de reserva y las alertas de stock
STORE_EMAIL = os.getenv("STORE_EMAIL", "minimarket.lostios@gmail.com")

# Claves reCaptcha (si no están en .env se usan las claves públicas de prueba de Google)
RECAPTCHA_PUBLIC_KEY = os.getenv("RECAPTCHA_PUBLIC_KEY") or "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"
RECAPTCHA_PRIVATE_KEY = os.getenv("RECAPTCHA_PRIVATE_KEY") or "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe"
# Silenciar advertencia de claves reCAPTCHA de prueba (solo desarrollo local)
SILENCED_SYSTEM_CHECKS = ['django_recaptcha.recaptcha_test_key_error']

JAZZMIN_SETTINGS = {
    "site_title": "Almacén Los Tíos",
    "site_header": "Almacén Los Tíos",
    "site_brand": "Almacén Los Tíos",
    "welcome_sign": "Panel administrativo",
    "show_ui_builder": False,
    "order_with_respect_to": ["productos", "venta", "usuarios"],
}
