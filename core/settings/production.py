from .base import *  # noqa

###################################################################
# General
###################################################################

DEBUG = False

###################################################################
# Django security
###################################################################

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = ["https://panel.kelajakmediklari.uz", "https://kelajakmediklari.uz",
                        "https://testkm.kelajakmediklari.uz", "http://localhost:3000"]

###################################################################
# CORS
###################################################################

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = ["*"]

# CORS CONFIGURATION for HLS Streaming
CORS_ALLOW_ALL_ORIGINS = True  # Set to False in production and use CORS_ALLOWED_ORIGINS
CORS_ALLOW_CREDENTIALS = True

# Headers needed for HLS video streaming
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "range",  # Required for video streaming
]

# Expose headers needed for HLS streaming
CORS_EXPOSE_HEADERS = [
    "content-range",
    "accept-ranges",
    "content-length",
    "content-type",
]

# Allow methods for CORS
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]


REDIS_HOST = env.str("REDIS_HOST", "redis")
REDIS_PORT = env.int("REDIS_PORT", 6379)
REDIS_DB = env.int("REDIS_DB", 0)
