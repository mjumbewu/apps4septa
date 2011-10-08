Installation
============

Follow the instructions to install GeoDjango at https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/.

Copy the ``settings/local.py.template`` file to ``settings/local.py`` and fill in the settings for your PostGIS database with the SEPTA data.  Also, fill in some random data for the site secret key.

Run ``python manage.py syncdb``.
