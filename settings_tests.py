DATABASES={
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
MIDDLEWARE_CLASSES=()
INSTALLED_APPS=(
    'ttag',
    "django.contrib.auth",
    "django.contrib.contenttypes",
    'django.contrib.sessions',
)
SITE_ID=1
SECRET_KEY='super-secret'
ROOT_URLCONF=''
