from .base import *  # noqa

###################################################################
# General
###################################################################

DEBUG = False

###################################################################
# Django security
###################################################################

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO")
CORS_ORIGIN_ALLOW_ALL = True
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = ["https://panel.kelajakmediklari.uz", "https://kelajakmediklari.uz",
                        "https://testkm.kelajakmediklari.uz", "http://localhost:3000"]

###################################################################
# CORS
###################################################################

# When credentials are allowed, you must explicitly list allowed origins
CORS_ALLOW_HEADERS = ["*"]
CORS_ALLOW_CREDENTIALS = True

REDIS_HOST = env.str("REDIS_HOST", "redis")
REDIS_PORT = env.int("REDIS_PORT", 6379)
REDIS_DB = env.int("REDIS_DB", 0)
