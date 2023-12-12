import dj_database_url

ALLOWED_HOSTS = ["*"]

# Modules in use, commented modules that you won't use
MODULES = [
    'authentication',
    'base',
    'booth',
    'census',
    'mixnet',
    'postproc',
    'store',
    'visualizer',
    'voting',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
]

base_url = 'http://localhost:8000'


APIS = {
    'authentication': base_url,
    'base': base_url,
    'booth': base_url,
    'census': base_url,
    'mixnet': base_url,
    'postproc': base_url,
    'store': base_url,
    'visualizer': base_url,
    'voting': base_url,
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'decidedb',
#         'USER': 'decideuser',
#         'PASSWORD': 'decidepass123',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }
DATABASES = {
    'default': dj_database_url.config(
        default="postgres://admin:a7qrFICWjm4gjSIRPbVWaAtvjzernCyg@dpg-clqtjgqe9h4c73aq41fg-a.oregon-postgres.render.com/decidedb_ksdl",
        conn_max_age=600
    )
}


# number of bits for the key, all auths should use the same number of bits
KEYBITS = 256
