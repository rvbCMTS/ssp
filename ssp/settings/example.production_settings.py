from .base_settings import BASE_DIR


# Replace with custom secret key for security
SECRET_KEY = 'slvfnq+rsg$-mkh+(5f*jutuhf2)_tmuq&__yzicnn6hpb*hrm'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydatabase',
        'USER': 'mydatabaseuser',
        'PASSWORD': 'mypassword',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}


PERSONNEL_DOSIMETRY_DIRS = {
    'Landauer': {
        'incoming': '<path-to-incoming-directory-for-Landauer-reports>',
        'outgoing': '<path-to-outgoing-directory-for-Landauer-reports>'
    }
}
