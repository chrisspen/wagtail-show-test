from .base import *

DEBUG = True

ALLOWED_HOSTS = ["*"]

# Disable CSRF for dev to allow any domain
MIDDLEWARE = [m for m in MIDDLEWARE if m != "django.middleware.csrf.CsrfViewMiddleware"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
