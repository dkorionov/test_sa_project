from sa_project.settings import config

SECRET_KEY = config('SECRET_KEY')
ROOT_URLCONF = 'sa_project.urls'

WSGI_APPLICATION = 'sa_project.wsgi.application'
ASGI_APPLICATION = 'sa_project.asgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.oauth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.oauth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.oauth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.oauth.password_validation.NumericPasswordValidator',
    },
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
