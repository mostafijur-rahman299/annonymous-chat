
import environ

env = environ.Env()
environ.Env.read_env()

if env('ENVIRONMENT') == 'production':
    from .production import *
else:
    from .development import *
