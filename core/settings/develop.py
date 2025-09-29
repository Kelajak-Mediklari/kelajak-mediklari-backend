from .base import *  # noqa

DEBUG = True
CELERY_TASK_ALWAYS_EAGER = False

# CORS for local development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_CREDENTIALS = True
