from .base import *

from decouple import config


DEBUG = False


# ALLOWED_HOSTS = ['.entryarea.com']

ALLOWED_HOSTS = ['entryarea.com', 'en.entryarea.com', 'tr.entryarea.com']

SESSION_COOKIE_DOMAIN = '.entryarea.com'

ADMINS = [('oguz', 'goeswog@gmail.com')]

# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_USE_TLS = config('EMAIL_USE_TLS')
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_PORT = config('EMAIL_PORT')



