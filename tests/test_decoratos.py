#: TODO TestIsolatedAccessByRoleDecorator.test_simple_preserve_attributes will
#: TODO not pass if django.utils.decorators.method_decorator is used
#: TODO Implements test with dummy view class
import unittest
try:
    from unittest.mock import Mock, patch
except:
    from mock import Mock, patch
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import user_passes_test, login_required, \
    permission_required
from django.utils.decorators import method_decorator
from roles.decorators import access_by_role

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
