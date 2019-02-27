from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', 'en.localhost.com', 'tr.localhost.com',
                 'de.localhost.com', '127.0.0.1', '192.168.43.241',
                 ]

INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

INTERNAL_IPS = ALLOWED_HOSTS



