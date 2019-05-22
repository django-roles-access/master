import unittest
from django.conf import settings
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model

try:
    from unittest.mock import Mock, patch
except:
    from mock import Mock, patch

from tests.views import ProtectedMixinView

User = get_user_model()


# UNIT TEST
class TestUnitRolesMixin(unittest.TestCase):

    def test_preserve_attributes(
            self
    ):
        dispatched = ProtectedMixinView().dispatch
        self.assertIs(getattr(dispatched, 'access_by_role',
                      False), True)


# INTEGRATED TEST
class TestIntegratedRolesMixin(TestCase):

    def setUp(self):
        settings.__setattr__('SECURED', ['django_roles_access'])
        # User
        self.u1, created = User.objects.get_or_create(username='test-1')

    def tearDown(self):
        settings.__delattr__('SECURED')

    def test_get_access_class_view(self):
        self.client.force_login(self.u1)
        response = self.client.get(
            '/role-included2/mixin_class_view/')
        self.assertEqual(response.status_code, 200)

    def test_get_access_denied_class_view(self):
        self.client.logout()
        response = self.client.get(
            '/role-included2/mixin_class_view/')
        self.assertEqual(response.status_code, 403)
