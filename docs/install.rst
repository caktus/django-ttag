============
Installation
============

Before installing django-ttag, you'll obviously need to have copy of Django
installed. For the |version| release, Django 1.4-1.8 and Python 2.6 or 2.7
are required.


Installing django-ttag
======================

The easiest way is to use an automatic package-installation tools like pip__.

.. __: http://pip.openplans.org/

Simply type::

    pip install django-ttag

Manual installation
-------------------

If you prefer not to use an automated package installer, you can
download a copy of django-ttag and install it manually. The
latest release package can be downloaded from `django-ttag's
listing on the Python Package Index`__.

.. __: http://pypi.python.org/pypi/django-ttag/

Once you've downloaded the package, unpack it and run the ``setup.py``
installation script::

    python setup.py install


Configuring your project
========================

There is nothing you need to do to configure django-ttag with your Django
project. Once it's installed, just :doc:`start using it <usage>`!

If, however you would like to run the standard django-ttag tests as part of
your project tests then you can. In your  project's settings module,
add django-ttag to your ``INSTALLED_APPS`` setting::
    
    INSTALLED_APPS = (
        ...
        'ttag',
    )
