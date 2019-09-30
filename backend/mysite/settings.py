import os

import yaml


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


config_file = os.getenv('SETTINGS_FILE')
with open(config_file) as f:
    attrs = yaml.safe_load(f.read())


# Параметры для части приложения по работе с аккаунтами
TOKEN_LINK = (
    f"https://oauth.vk.com/authorize?"
    f"client_id={attrs['VK_ROOT']['ID']}"
    f"&scope={attrs['VK_ROOT']['SCOPE']}"
    f"&response_type=token&v={attrs['VK_ROOT']['VERSION']}"
)

SECRET_KEY = attrs['SECRET_KEY']
VK_SERVICE_KEY = attrs['VK_APP']['SERVICE']
DEBUG = attrs['DEBUG']

ALLOWED_HOSTS = attrs['ALLOWED_HOSTS']

# Настройки авторизации через VK

APP_BASE_URL = attrs['APP_BASE_URL']

# Application definition
ROOT_URLCONF = 'mysite.urls'
WSGI_APPLICATION = 'mysite.wsgi.application'


# Internationalization
LANGUAGE_CODE = 'ru-rus'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'stats', 'static'),
)


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'stats.apps.StatsConfig',
    'rest_framework'
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


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'stats.auth.VkSessionAuthentication',
    )
}


TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request'
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['./stats/templates/'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages'
            ],
        },
    },
]


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': attrs['DATABASE']['NAME'],
        'USER': attrs['DATABASE']['USER'],
        'PASSWORD': attrs['DATABASE']['PASSWORD'],
        'HOST': attrs['DATABASE']['HOST'],
        'PORT': attrs['DATABASE']['PORT']
    }
}


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
