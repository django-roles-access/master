import unittest

from django.conf import settings
from django.test import TestCase, override_settings

try:
    from unittest.mock import Mock, patch
except:
    from mock import Mock, patch
from django.contrib.auth import get_user_model

User = get_user_model()


# INTEGRATED TEST
@override_settings(ROOT_URLCONF='tests.urls')
class TestIntegratedRolesMixin(TestCase):

    def setUp(self):
        settings.__setattr__('SECURED', ['roles'])
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
