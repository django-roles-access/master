import os
import sys
import django
from django.conf import settings

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings_test')
os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'


def pytest_configure():
    settings.LANGUAGE_CODE = 'en'
    settings.DEBUG = False
    # Because some test run only with pytest.
    sys._called_from_pytest = True
    django.setup()


def pytest_unconfigure(config):
    # Delete created variable for detect if running with pytest.
    del sys._called_from_pytest
