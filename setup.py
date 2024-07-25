from setuptools import setup
from ttag import get_version

setup(
    name='django-ttag',
    version=get_version(),
    description="A template tag constructor library for Django.",
    long_description=open('README.rst').read(),
    author='Chris Beaven',
    author_email='chris@lincolnloop.com',
    license='MIT',
    url='http://github.com/lincolnloop/django-ttag',
    install_requires=[
        'six',
    ],
    packages=[
        'ttag',
        'ttag.tests',
        'ttag.tests.ttag_test_app',
        'ttag.tests.ttag_test_app.templatetags',
        'ttag.tests.ttag_test_app.templatetags.ttag_test',
        'ttag.helpers',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Framework :: Django',
    ],
)
