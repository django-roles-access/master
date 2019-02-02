from django.apps import apps
from django.test import TestCase
from django_roles.apps import RolesConfig


class ReportsConfigTest(TestCase):
    def test_apps(self):
        # Test the class
        self.assertEqual(RolesConfig.name, 'django_roles')
        self.assertEqual(RolesConfig.verbose_name, u'Django Roles')

        # Test the app
        self.assertEqual(apps.get_app_config('django_roles').name,
                         'django_roles')
