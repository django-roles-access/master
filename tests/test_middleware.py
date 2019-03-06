import unittest

from django.core.exceptions import PermissionDenied

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

    @patch('django_roles.middleware.check_access_by_role')
    def test_middleware(
            self, mock_check_access_by_role
    ):
        response = self.middleware(self.request)
        assert response.django_roles

    @patch('django_roles.middleware.check_access_by_role')
    def test_middleware_call_check_access_by_role(
            self, mock_check_access_by_role
    ):
        self.middleware(self.request)
        assert mock_check_access_by_role.called
        self.assertEqual(mock_check_access_by_role.call_count, 1)

    @patch('django_roles.middleware.check_access_by_role')
    def test_middleware_call_check_access_by_roles_with_request(
            self, mock_check_access_by_role
    ):
        self.middleware(self.request)
        mock_check_access_by_role.assert_called_once_with(self.request)

    @patch('django_roles.middleware.check_access_by_role')
    def test_middleware_raise_permission_denied_if_not_check_access(
            self, mock_check_access_by_role
    ):
        mock_check_access_by_role.return_value = False
        with self.assertRaises(PermissionDenied):
            self.middleware(self.request)

    @patch('django_roles.middleware.check_access_by_role')
    def test_middleware_get_response(
            self, mock_check_access_by_role
    ):
        self.middleware(self.request)
        self.middleware.get_response.assert_called_once_with(self.request)

    @patch('django_roles.middleware.check_access_by_role')
    def test_middleware_return_response_with_request(
            self, mock_check_access_by_role
    ):
        def func(param):
            return param
        self.middleware.get_response.side_effect = func
        response = self.middleware(self.request)
        assert response == func(self.request)


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
