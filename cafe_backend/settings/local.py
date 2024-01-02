from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

DATABASES = get_secret('DATABASES')

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://localhost:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": "changeme"
        }
    }
    # "replica": {
    #     "BACKEND": "django_redis.cache.RedisCache",
    #     "LOCATION": "redis://redis-slave:6379/0",
    #     "OPTIONS": {
    #         "CLIENT_CLASS": "django_redis.client.DefaultClient",
    #     }
    # }
}