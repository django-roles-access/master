#: TODO: UnitTest must be implemented using mock and checking called_once_with

import unittest
try:
    from unittest.mock import Mock, patch
except:
    from mock import Mock, patch

from django.conf import settings
from django.test import TestCase, RequestFactory, \
    modify_settings, override_settings
from django.contrib.auth import get_user_model

from django_roles.middleware import RolesMiddleware
User = get_user_model()


# UNIT TEST
class MiddlewareUnitTest(unittest.TestCase):

    def setUp(self):
        self.request = RequestFactory()
        self.request.path_info = Mock()
        self.request.user = Mock()
        self.middleware = RolesMiddleware(Mock())

    def test_init(self):
        init_result = RolesMiddleware('response')
        assert init_result.get_response == 'response'

    @patch('django_roles.tools.resolve')
    @patch('django_roles.tools.ViewAccess')
    def test_middleware(
            self, mock_view_acces, mock_resolve
    ):
        response = self.middleware(self.request)
        assert response.django_roles


# INTEGRATED TEST
@modify_settings(MIDDLEWARE={
    'append': 'django_roles.middleware.RolesMiddleware'
})
class MiddlewareIntegratedTestSecuredApp(TestCase):

    def setUp(self):
        settings.__setattr__('SECURED', ['django_roles'])
        # User
        self.u1, created = User.objects.get_or_create(username='test-1')

    def tearDown(self):
        settings.__delattr__('SECURED')

    def test_get_access_view_function(self):
        self.client.force_login(self.u1)
        response = self.client.get(
            '/role-included2/middleware_view_func/')
        self.assertEqual(response.status_code, 200)

    def test_get_access_denied_view_function(self):
        self.client.logout()
        response = self.client.get(
            '/role-included2/middleware_view_func/')
        self.assertEqual(response.status_code, 403)

    def test_get_access_class_view(self):
        self.client.force_login(self.u1)
        response = self.client.get(
            '/role-included2/middleware_view_class/')
        self.assertEqual(response.status_code, 200)

    def test_get_access_denied_class_view(self):
        self.client.logout()
        response = self.client.get(
            '/role-included2/middleware_view_class/')
        self.assertEqual(response.status_code, 403)
