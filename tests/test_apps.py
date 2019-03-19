from django.apps import apps
from django.test import TestCase
from django_roles_access.apps import RolesConfig


class ReportsConfigTest(TestCase):
    def test_apps(self):
        # Test the class
        self.assertEqual(RolesConfig.name, 'django_roles_access')
        self.assertEqual(RolesConfig.verbose_name, u'Django Roles Access')

        # Test the app
        self.assertEqual(apps.get_app_config('django_roles_access').name,
                         'django_roles_access')
