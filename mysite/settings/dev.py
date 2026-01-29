from .base import *

DEBUG = True

ALLOWED_HOSTS = ["*"]


# Middleware to forcefully disable CSRF checks
class DisableCSRF:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        setattr(request, "_dont_enforce_csrf_checks", True)
        return self.get_response(request)


MIDDLEWARE = [
    "mysite.settings.dev.DisableCSRF",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
