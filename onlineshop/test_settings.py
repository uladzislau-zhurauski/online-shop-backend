from .settings import *  # NOQA

# change the database if necessary
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': ':memory:'
#     }
# }

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
