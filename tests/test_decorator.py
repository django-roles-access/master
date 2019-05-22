import unittest
from django.conf import settings
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import (user_passes_test,
                                            login_required,
                                            permission_required)
try:
    from unittest.mock import Mock, patch, MagicMock
except:
    from mock import Mock, patch

from django_roles_access.models import ViewAccess
from django_roles_access.decorator import access_by_role
from django_roles_access.tools import DEFAULT_FORBIDDEN_MESSAGE

User = get_user_model()


def myattr_dec(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    wrapper.myattr = True
    return wrapper


class TestAccessByRoleWithOtherDecorators(unittest.TestCase):

    def test_view_is_decorated_with_access_by_role(self):
        from .views import protected_view_by_role
        self.assertTrue(protected_view_by_role.access_by_role)

    def test_attributes(self):
        doc = "Check if logged user can access the decorated function or " \
              "method."
        self.assertEqual(access_by_role.__name__, 'access_by_role')
        self.assertIn(doc, access_by_role.__doc__)
        self.assertEqual(access_by_role.__dict__, {})

    def test_simple_preserve_attributes_with_other_decorator(self):
        @access_by_role
        def func():
            pass
        self.assertIs(getattr(func, 'access_by_role', False), True)

        @access_by_role
        @myattr_dec
        def func():
            pass

        self.assertIs(getattr(func, 'myattr', False), True)
        self.assertIs(getattr(func, 'access_by_role', False), True)

    def test_preserve_attributes_with_contrib_user_passes_test(self):

        def challenge(user):
            return True

        @access_by_role
        @user_passes_test(challenge)
        def func():
            pass
        self.assertIs(getattr(func, 'access_by_role', False), True)

    def test_preserve_attributes_with_contrib_login_required(self):
        @login_required
        @access_by_role
        def func():
            pass
        self.assertIs(getattr(func, 'access_by_role', False), True)

    def test_preserve_attributes_with_contrib_permission_required(self):
        @permission_required(Mock())
        @access_by_role
        def func():
            pass
        self.assertIs(getattr(func, 'access_by_role', False), True)

    def test_preserve_attribute_decorating_class_method(self):

        class DummyClass(object):
            @access_by_role
            def method(self):
                pass
        self.assertIs(getattr(DummyClass().method, 'access_by_role', False),
                      True)


class UnitTestAccessByRoleDecorator(unittest.TestCase):

    @patch('django_roles_access.decorator.check_access_by_role')
    def test_decorator_call_check_access_by_role(
            self, mock_check_access_by_role
    ):
        func = Mock()
        func.__name__ = 'func'  # Needed by Python 2.7
        request = Mock()
        decorated_func = access_by_role(func)
        decorated_func(request)
        assert mock_check_access_by_role.called

    @patch('django_roles_access.decorator.check_access_by_role')
    def test_decorator_call_check_access_by_role_with_request(
            self, mock_check_access_by_role
    ):
        func = Mock()
        func.__name__ = 'func'  # Needed by Python 2.7
        request = Mock()
        decorated_func = access_by_role(func)
        decorated_func(request)
        mock_check_access_by_role.assert_called_once_with(request)

    @patch('django_roles_access.decorator.check_access_by_role')
    def test_decorator_return_view_if_access_by_role_return_true(
            self, mock_check_access_by_role
    ):
        func = Mock()
        func.__name__ = 'func'  # Needed by Python 2.7
        request = Mock()
        decorated_func = access_by_role(func)
        mock_check_access_by_role.return_value = True
        response = decorated_func(request)
        assert response == func(request)

    @patch('django_roles_access.decorator.get_no_access_response')
    @patch('django_roles_access.decorator.check_access_by_role')
    def test_call_get_no_access_response_when_access_by_role_return_false(
            self, mock_check_access_by_role, mock_get_no_access_response
    ):
        func = Mock()
        func.__name__ = 'func'  # Needed by Python 2.7
        request = Mock()
        decorated_func = access_by_role(func)
        mock_check_access_by_role.return_value = False
        decorated_func(request)
        assert mock_get_no_access_response.called

    @patch('django_roles_access.decorator.get_no_access_response')
    @patch('django_roles_access.decorator.check_access_by_role')
    def test_call_once_get_no_access_response_when_access_by_role_return_false(
            self, mock_check_access_by_role, mock_get_no_access_response
    ):
        func = Mock()
        func.__name__ = 'func'  # Needed by Python 2.7
        request = Mock()
        decorated_func = access_by_role(func)
        mock_check_access_by_role.return_value = False
        decorated_func(request)
        assert mock_get_no_access_response.call_count == 1


class IntegratedTestAccessByRoleDecorator(TestCase):
    """
    Integrated Test using default behavior for SECURED applications.
    """

    def setUp(self):
        settings.__setattr__('SECURED', ['django_roles_access'])
        # User
        self.u1, created = User.objects.get_or_create(username='test-1')

    def tearDown(self):
        settings.__delattr__('SECURED')

    def test_get_200_status_with_view_function(self):
        self.client.force_login(self.u1)
        response = self.client.get(
            '/role-included2/view_by_role/')
        self.assertEqual(response.status_code, 200)

    def test_get_403_status_with_view_function(self):
        self.client.logout()
        response = self.client.get(
            '/role-included2/view_by_role/')
        self.assertEqual(response.status_code, 403)

    def test_get_200_status_with_class_view(self):
        self.client.force_login(self.u1)
        response = self.client.get(
            '/role-included2/view_by_role_class/')
        self.assertEqual(response.status_code, 200)

    def test_get_403_status_with_class_view(self):
        self.client.logout()
        response = self.client.get(
            '/role-included2/view_by_role_class/')
        self.assertEqual(response.status_code, 403)

    def test_get_200_status_with_direct_view(self):
        """
        A view without URLConf application
        """
        ViewAccess.objects.create(
            view='direct_access_view',
            type='au'
        )
        self.client.force_login(self.u1)
        response = self.client.get(
            '/direct_access_view/')
        self.assertEqual(response.status_code, 200)

    def test_get_403_status_with_direct_view(self):
        ViewAccess.objects.create(
            view='direct_access_view',
            type='au'
        )
        self.client.logout()
        response = self.client.get(
            '/direct_access_view/')
        self.assertEqual(response.status_code, 403)

    def test_default_behavior_when_no_configuration(self):
        """
        Default behavior is to remain public if Django Roles si installed but
        no more configuration or decorator is used.
        """
        self.client.logout()
        response = self.client.get(
            '/direct_view/')
        self.assertEqual(response.status_code, 200)

    def test_forbidden_behavior_without_configuration(self):
        self.client.logout()
        response = self.client.get(
            '/role-included2/view_by_role/')
        self.assertIn(DEFAULT_FORBIDDEN_MESSAGE, response.content.decode(
            'utf-8'))

    def test_forbidden_behavior_with_configuration(self):
        expected = '<h1>No access</h1><p>Contact administrator</p>'
        settings.__setattr__('DJANGO_ROLES_ACCESS_FORBIDDEN_MESSAGE',
                             expected)
        self.client.logout()
        response = self.client.get(
            '/role-included2/view_by_role/')
        settings.__delattr__('DJANGO_ROLES_ACCESS_FORBIDDEN_MESSAGE')
        self.assertIn(expected, response.content.decode('utf-8'))

    def test_redirect_if_configured(self):
        settings.__setattr__('DJANGO_ROLES_ACCESS_REDIRECT', True)
        self.client.logout()
        response = self.client.get(
            '/role-included2/view_by_role/')
        settings.__delattr__('DJANGO_ROLES_ACCESS_REDIRECT')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, settings.LOGIN_URL)
