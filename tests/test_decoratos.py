#: TODO TestIsolatedAccessByRoleDecorator.test_simple_preserve_attributes will
#: TODO not pass if django.utils.decorators.method_decorator is used
#: TODO Implements test with dummy view class
#: TODO: Test decorator with direct view.
#: TODO: UnitTest must be implemented using mock and checking called_once_with
import unittest

from django.conf import settings
from django.test import TestCase, override_settings

try:
    from unittest.mock import Mock, patch, MagicMock
except:
    from mock import Mock, patch
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import user_passes_test, login_required, \
    permission_required
from django.utils.decorators import method_decorator
from django_roles.decorators import access_by_role

User = get_user_model()


def myattr_dec(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    wrapper.myattr = True
    return wrapper


class TestIsolatedAccessByRoleDecorator(unittest.TestCase):

    def test_attributes(self):
        doc = "Check if logged user can access the decorated function or class."
        self.assertEqual(access_by_role.__name__, 'access_by_role')
        self.assertIn(doc, access_by_role.__doc__)
        self.assertEqual(access_by_role.__dict__, {})

    def test_simple_preserve_attributes(self):
        # Sanity check myattr_dec
        @myattr_dec
        def func():
            pass
        self.assertIs(getattr(func, 'myattr', False), True)

        @access_by_role
        def func():
            pass
        self.assertIs(getattr(func, 'access_by_role', False), True)

        @method_decorator(myattr_dec)
        # @myattr_dec  # Do not pass!!
        @access_by_role
        def func():
            pass

        self.assertIs(getattr(func, 'myattr', False), True)
        self.assertIs(getattr(func, 'access_by_role', False), True)

        @method_decorator(access_by_role)
        # @access_by_role  Do not pass!!
        @myattr_dec
        def func():
            pass

        self.assertIs(getattr(func, 'myattr', False), True)
        self.assertIs(getattr(func, 'access_by_role', False), True)

    def test_preserve_attributes_with_contrib_user_passes_test(self):

        def challenge(user):
            return True

        @access_by_role
        def func():
            pass
        self.assertIs(getattr(func, 'access_by_role', False), True)

        @user_passes_test(challenge)
        @access_by_role
        def func():
            pass
        self.assertIs(getattr(func, 'access_by_role', False), True)

    def test_preserve_attributes_with_contrib_login_required(self):
        @access_by_role
        def func():
            pass
        self.assertIs(getattr(func, 'access_by_role', False), True)

        @login_required
        @access_by_role
        def func():
            pass
        self.assertIs(getattr(func, 'access_by_role', False), True)

    def test_preserve_attributes_with_contrib_permission_required(self):
        @access_by_role
        def func():
            pass
        self.assertIs(getattr(func, 'access_by_role', False), True)

        @permission_required(Mock())
        @access_by_role
        def func():
            pass
        self.assertIs(getattr(func, 'access_by_role', False), True)

    def test_preserve_attribute_decorating_class(self):
        @access_by_role
        class DummyClass(object):
            pass
        self.assertIs(getattr(DummyClass, 'access_by_role', False), True)

    def test_preserve_attribute_decorating_class_method(self):

        class DummyClass(object):
            @access_by_role
            def method(self):
                pass
        self.assertIs(getattr(DummyClass().method, 'access_by_role', False),
                      True)

    @patch('django_roles.decorators.check_access_by_role')
    def test_decorator_call_check_access_by_role(
            self, mock_check_access_by_role
    ):
        request = Mock()
        view = MagicMock(name='_view')
        # mock_check_access_by_role._view.side_effect = view(request)
        mock_check_access_by_role._view.return_value = view(request)

        access_by_role(view=view)

        mock_check_access_by_role.assert_called()

    # @patch('django_roles.decorators.check_access_by_role')
    # def test_decorator_call_check_access_by_role_with_request(
    #         self, mock_check_access_by_role
    # ):
    #     request = Mock()
    #     view = Mock()
    #
    #     @access_by_role(view=view)
    #     def func():
    #         pass
    #     func()
    #     mock_check_access_by_role.assert_called_with(request)

# INTEGRATED TEST
class TestIntegratedAccessByRoleDecorator(TestCase):

    def setUp(self):
        settings.__setattr__('SECURED', ['django_roles'])
        # User
        self.u1, created = User.objects.get_or_create(username='test-1')

    def tearDown(self):
        settings.__delattr__('SECURED')

    def test_get_access_view_function(self):
        self.client.force_login(self.u1)
        response = self.client.get(
            '/role-included2/view_by_role/')
        self.assertEqual(response.status_code, 200)

    def test_get_access_denied_view_function(self):
        self.client.logout()
        response = self.client.get(
            '/role-included2/view_by_role/')
        self.assertEqual(response.status_code, 403)

    def test_get_access_class_view(self):
        self.client.force_login(self.u1)
        response = self.client.get(
            '/role-included2/view_by_role_class/')
        self.assertEqual(response.status_code, 200)

    def test_get_access_denied_class_view(self):
        self.client.logout()
        response = self.client.get(
            '/role-included2/view_by_role_class/')
        self.assertEqual(response.status_code, 403)
