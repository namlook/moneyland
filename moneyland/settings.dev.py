
from .settings import *

INSTALLED_APPS.append('debug_toolbar')

MIDDLEWARE = [ 'debug_toolbar.middleware.DebugToolbarMiddleware' ] + MIDDLEWARE
