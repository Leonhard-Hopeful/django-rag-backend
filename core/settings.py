"""
Django settings for the 'core' project.

This settings file is configured for both local development and production deployment on Heroku.
It reads sensitive information and environment-specific configurations from environment variables.
"""

import os
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from a .env file if it exists.
# This is primarily for local development.
load_dotenv(os.path.join(BASE_DIR, ".env"))

# --- SECURITY SETTINGS ---
# Best Practice: Load the SECRET_KEY from an environment variable.
# NEVER commit the secret key to version control.
# On Heroku, this will be set as a "Config Var".
SECRET_KEY = os.environ.get('SECRET_KEY')

# Best Practice: DEBUG should be False in production for security.
# We set it to True only if a 'DEVELOPMENT' environment variable is explicitly set.
# Heroku will not have this variable, so DEBUG will correctly be False.
DEBUG = 'DEVELOPMENT' in os.environ

# Configure allowed hosts.
# In production, Heroku provides the hostname as an environment variable.
ALLOWED_HOSTS = []
HEROKU_APP_HOST = os.environ.get('HEROKU_APP_HOST')
if HEROKU_APP_HOST:
    ALLOWED_HOSTS.append(HEROKU_APP_HOST)
if DEBUG:
    ALLOWED_HOSTS.extend(['127.0.0.1', 'localhost'])


# --- APPLICATION DEFINITION ---
# Add your apps and third-party apps here.
INSTALLED_APPS = [
    # WhiteNoise must be listed before all other apps except django.contrib.staticfiles
    'whitenoise.runserver_nostatic',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'corsheaders',

    # Your local apps
    'api.apps.ApiConfig', # Or simply 'api'
]

# --- MIDDLEWARE CONFIGURATION ---
# The order of middleware is important.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise middleware should be placed right after the security middleware.
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # CORS middleware should be placed high up, before CommonMiddleware.
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# --- DATABASE CONFIGURATION ---
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
# This configuration uses dj-database-url to read the DATABASE_URL environment variable
# provided by Heroku. For local development, it falls back to the SQLite database.
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{os.path.join(BASE_DIR, "db.sqlite3")}',
        conn_max_age=600,
        ssl_require=not DEBUG # SSL is required for Heroku Postgres, but not for local SQLite
    )
}


# --- PASSWORD VALIDATION ---
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# --- INTERNATIONALIZATION ---
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# --- STATIC FILES (CSS, JavaScript, Images) ---
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = '/static/'
# This is the directory where `collectstatic` will gather all static files for production.
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# This tells WhiteNoise to use a more efficient storage backend.
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# --- DEFAULT PRIMARY KEY FIELD ---
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- CORS (Cross-Origin Resource Sharing) SETTINGS ---
# This controls which frontend domains are allowed to make requests to our Django API.
# We load this from an environment variable for flexibility.
FRONTEND_URL = os.environ.get('FRONTEND_URL')
if FRONTEND_URL:
    CORS_ALLOWED_ORIGINS = [FRONTEND_URL]
elif DEBUG:
    # In local development, allow the default Vite and other common local hosts.
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]