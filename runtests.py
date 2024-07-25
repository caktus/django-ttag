#!/usr/bin/env python
import sys

from django.conf import settings

if not settings.configured:
    settings.configure(
        DATABASE_ENGINE='sqlite3',
        DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3'}},
        TEMPLATES=[{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'APP_DIRS': True,
        }],
        INSTALLED_APPS=[
            'ttag',
            'ttag.tests.ttag_test_app'
        ],
        DEFAULT_AUTO_FIELD='django.db.models.AutoField',
    )

try:
    # Django <= 1.8
    from django.test.simple import DjangoTestSuiteRunner
    test_runner = DjangoTestSuiteRunner(verbosity=1)
except ImportError:
    # Django >= 1.8
    import django
    django.setup()
    from django.test.runner import DiscoverRunner
    test_runner = DiscoverRunner(verbosity=1)

import ttag.tests.ttag_test_app.tags   # noqa: Import so tags can self register


def runtests(*test_args):
    if not test_args:
        test_args = ['ttag']
    failures = test_runner.run_tests(test_args)
    sys.exit(failures)


if __name__ == '__main__':
    runtests(*sys.argv[1:])
