from .base import *

DEBUG = True

SESSION_COOKIE_DOMAIN = '.localhost.com'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_USE_TLS = config('EMAIL_USE_TLS')
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_PORT = config('EMAIL_PORT')

ALLOWED_HOSTS = ['localhost', 'en.localhost.com', 'tr.localhost.com',
                 'de.localhost.com', '127.0.0.1', '192.168.43.241',
                 ]

INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

INTERNAL_IPS = ALLOWED_HOSTS


# Simple sqlite3 database connection
# Note: Faster than postgresql in localhost
'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
'''
