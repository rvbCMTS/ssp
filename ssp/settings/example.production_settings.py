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

FRONT_PAGE_PARAMETERS = {
    'OrganisationName': '<custom-organisation-name>',
    'ContactInformation': [
        {
            'Name': '<Contact-Name-1>',
            'Email': '<Contact-Email-1>'
        },
    ]
}


PERSONNEL_DOSIMETRY_DIRS = {
    'Landauer': {
        'incoming': '<path-to-incoming-directory-for-Landauer-reports>',
        'outgoing': '<path-to-outgoing-directory-for-Landauer-reports>'
    }
}

FLUORO_TIME_DB_ENGINE = {
    'DRIVER': r'{ODBC Driver 13 for SQL Server}',
    'SERVER': r'<server-name>',
    'DATABASE': r'<db-name>',
    'Trusted_Connection': True,
    'UID': r'',
    'PWD': r''
}

FLUORO_TIME_ORBIT_TABLE = '<table/view-name-in-orbit>'

RADIOPHARMACEUTICAL_BASE_DIR = '<path-to-radiopharmaceutical-base-dir>'

# ---------------------------------- LDAP authentication ---------------------------------- #
# These settings will need to be changed for each installation
LDAP_AUTH_URL = "<LDAP-URL>"
LDAP_AUTH_USE_TLS = True  # Recommended to use TLS
LDAP_AUTH_SEARCH_BASE = "DC=vll,DC=se"  # E.g., "DC=<domain>,DC=<other-dc-setting>
LDAP_AUTH_ACTIVE_DIRECTORY_DOMAIN = '<AD-directoyr-domain>'
LDAP_AUTH_OBJECT_CLASS = "user"

# User model fields mapped to the LDAP
# attributes that represent them.
LDAP_AUTH_USER_FIELDS = {
    "username": "sAMAccountName",
    "email": "mail",
}
# A tuple of django model fields used to uniquely identify a user.
LDAP_AUTH_USER_LOOKUP_FIELDS = ("username",)
# Set connection/receive timeouts (in seconds) on the underlying `ldap3` library.
# LDAP_AUTH_CONNECT_TIMEOUT = None
# LDAP_AUTH_RECEIVE_TIMEOUT = None
#
LDAP_AUTH_FORMAT_USERNAME = "django_python3_ldap.utils.format_username_active_directory_principal"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django_python3_ldap": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },
}

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    "django_python3_ldap.auth.LDAPBackend",
)
# ----------------------------------------------------------------------------------------- #
