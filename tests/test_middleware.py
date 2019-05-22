import unittest

from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden, HttpResponseRedirect

from django_roles_access.tools import DEFAULT_FORBIDDEN_MESSAGE
try:
    from unittest.mock import Mock, patch
except:
    from mock import Mock, patch
from django.conf import settings
from django.test import TestCase, RequestFactory, \
    modify_settings, override_settings
from django.contrib.auth import get_user_model

from django_roles_access.middleware import RolesMiddleware

User = get_user_model()


# UNIT TEST
@patch('django_roles_access.middleware.check_access_by_role')
class MiddlewareUnitTest(unittest.TestCase):

    def setUp(self):
        self.request = RequestFactory()
        self.request.path_info = Mock()
        self.request.user = Mock()
        self.middleware = RolesMiddleware(Mock())

    def test_init(
            self, mock_check_access_by_role=None
    ):
        init_result = RolesMiddleware('response')
        assert init_result.get_response == 'response'

    def test_middleware(
            self, mock_check_access_by_role
    ):
        response = self.middleware(self.request)
        assert response.django_roles

    def test_middleware_call_check_access_by_role(
            self, mock_check_access_by_role
    ):
        self.middleware(self.request)
        assert mock_check_access_by_role.called
        self.assertEqual(mock_check_access_by_role.call_count, 1)

    def test_middleware_call_check_access_by_roles_with_request(
            self, mock_check_access_by_role
    ):
        self.middleware(self.request)
        mock_check_access_by_role.assert_called_once_with(self.request)

    def test_middleware_get_response(
            self, mock_check_access_by_role
    ):
        self.middleware(self.request)
        self.middleware.get_response.assert_called_once_with(self.request)

    def test_middleware_return_response_with_request(
            self, mock_check_access_by_role
    ):
        def func(param):
            return param
        self.middleware.get_response.side_effect = func
        response = self.middleware(self.request)
        assert response == func(self.request)

    def test_middleware_return_http_forbidden_if_not_check_access(
            self, mock_check_access_by_role
    ):
        mock_check_access_by_role.return_value = False
        response = self.middleware(self.request)
        self.assertIsInstance(response, HttpResponseForbidden)

    def test_middleware_redirect_if_not_check_access(
            self, mock_check_access_by_role
    ):
        settings.__setattr__('DJANGO_ROLES_ACCESS_REDIRECT', True)
        mock_check_access_by_role.return_value = False
        response = self.middleware(self.request)
        settings.__delattr__('DJANGO_ROLES_ACCESS_REDIRECT')
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertEqual(response.url, settings.LOGIN_URL)

    @patch('django_roles_access.middleware.get_no_access_response')
    def test_call_get_no_access_response_when_access_by_role_return_false(
            self, mock_get_no_access_response, mock_check_access_by_role
    ):
        mock_check_access_by_role.return_value = False
        self.middleware(self.request)
        assert mock_get_no_access_response.called

    @patch('django_roles_access.middleware.get_no_access_response')
    def test_call_once_get_no_access_response_when_access_by_role_return_false(
            self, mock_get_no_access_response, mock_check_access_by_role
    ):
        mock_check_access_by_role.return_value = False
        self.middleware(self.request)
        assert mock_get_no_access_response.call_count == 1


# INTEGRATED TEST
@modify_settings(MIDDLEWARE={
    'append': 'django_roles_access.middleware.RolesMiddleware'
})
class MiddlewareIntegratedTestSecuredApp(TestCase):

    def setUp(self):
        settings.__setattr__('SECURED', ['django_roles_access'])
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

    def test_default_behavior_when_no_configuration(self):
        settings.__delattr__('SECURED')
        self.client.logout()
        response = self.client.get(
            '/role-included2/middleware_view_func/')
        settings.__setattr__('SECURED', ['django_roles_access'])
        self.assertEqual(response.status_code, 200)

    def test_forbidden_behavior_without_configuration(self):
        self.client.logout()
        response = self.client.get(
            '/role-included2/middleware_view_func/')
        expected = DEFAULT_FORBIDDEN_MESSAGE
        self.assertIn(expected, response.content.decode('utf-8'))

    def test_forbidden_behavior_with_configuration(self):
        expected = '<h1>No access</h1><p>Contact administrator</p>'
        settings.__setattr__('DJANGO_ROLES_ACCESS_FORBIDDEN_MESSAGE', expected)
        self.client.logout()
        response = self.client.get(
            '/role-included2/middleware_view_func/')
        settings.__delattr__('DJANGO_ROLES_ACCESS_FORBIDDEN_MESSAGE')
        self.assertIn(expected, response.content.decode('utf-8'))

    def test_redirect_if_configured(self):
        settings.__setattr__('DJANGO_ROLES_ACCESS_REDIRECT', True)
        self.client.logout()
        response = self.client.get(
            '/role-included2/middleware_view_func/')
        settings.__delattr__('DJANGO_ROLES_ACCESS_REDIRECT')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, settings.LOGIN_URL)
