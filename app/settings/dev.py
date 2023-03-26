from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-2dzjnfo*q83hcht+o9e_^74xz1r5_&=2o9r5yqgzdkw8u@$b1x"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = ["https://*", "http://*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


try:
    from .local import *
except ImportError:
    pass
