DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'decide',
        'USER': 'decide',
        'PASSWORD': 'decide',
        'HOST': 'localhost',
        'PORT': 5432,
    }
}

STATIC_ROOT = '/home/decide/static/'
MEDIA_ROOT = '/home/decide/static/media/'
ALLOWED_HOSTS = ['*']
ALLOWED_ORIGINS = [
    'http://*',
    'https://*',
    'https://localhost:8080',
    'http://localhost:8080'
]
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_TRUSTED_ORIGINS = ALLOWED_ORIGINS.copy()

# Modules in use, commented modules that you won't use
MODULES = [
    'authentication',
    'base',
    'booth',
    'census',
    'configurator',
    'mixnet',
    'postproc',
    'store',
    'visualizer',
    'voting',
]

BASEURL = 'http://localhost:8000'

APIS = {
    'authentication': 'http://localhost:8000',
    'base': 'http://localhost:8000',
    'booth': 'http://localhost:8000',
    'census': 'http://localhost:8000',
    'configurator': 'http://localhost:8000',
    'mixnet': 'http://localhost:8000',
    'postproc': 'http://localhost:8000',
    'store': 'http://localhost:8000',
    'visualizer': 'http://localhost:8000',
    'voting': 'http://localhost:8000',
}
