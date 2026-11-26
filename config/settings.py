"""
Configuración del proyecto "Datos en Criollo".

Los valores sensibles o que cambian según el entorno (SECRET_KEY, DEBUG,
ALLOWED_HOSTS) se leen desde un archivo .env mediante python-decouple.
Ver .env.example para la lista de variables.
"""

from pathlib import Path

from decouple import Csv, config

# Todas las rutas se construyen a partir de BASE_DIR (sin rutas absolutas).
BASE_DIR = Path(__file__).resolve().parent.parent


# --- Seguridad ---------------------------------------------------------------

SECRET_KEY = config("SECRET_KEY")

DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="127.0.0.1,localhost", cast=Csv())


# --- Aplicaciones ------------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Apps del proyecto
    "posts",
    "usuarios",
    "sitio",
    "portafolio",
    "herramientas",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "posts.context_processors.categorias",
                "sitio.context_processors.perfil",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# --- Base de datos -----------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# --- Validación de contraseñas -----------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# --- Internacionalización ----------------------------------------------------

LANGUAGE_CODE = "es-ar"

TIME_ZONE = "America/Argentina/Buenos_Aires"

USE_I18N = True

USE_TZ = True


# --- Archivos estáticos y multimedia -----------------------------------------

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"  # destino de collectstatic (despliegue)

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"  # imágenes subidas por los usuarios


# --- Autenticación -----------------------------------------------------------

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "lista_posts"
LOGOUT_REDIRECT_URL = "lista_posts"


# --- Correo -------------------------------------------------------------------
# Sin configuración, los correos se muestran en la terminal (útil en desarrollo).
# Para enviarlos de verdad, definí EMAIL_HOST y las demás variables en el .env.

EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_BACKEND = (
    "django.core.mail.backends.smtp.EmailBackend"
    if EMAIL_HOST
    else "django.core.mail.backends.console.EmailBackend"
)
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="Datos en Criollo <no-responder@localhost>")


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
