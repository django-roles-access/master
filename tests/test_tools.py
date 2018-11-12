"""
The classes contained in this file:

* GetInstalledApp<Test>: Are the classes used for testing
  :func:`Role.utils.get_installed_app`.


"""
import unittest

import pytest
from django.conf import settings
from django.contrib.auth import logout, login
from django.contrib.auth.models import User, Group
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory, modify_settings, override_settings, \
    TestCase

from roles.models import ViewAccess
from roles.tools import get_setting_dictionary, get_view_access, \
    check_access_by_role


@pytest.mark.django_db
class TestGetViewAccess(unittest.TestCase):

    def setUp(self):
        # User and group
        self.u1, created = User.objects.get_or_create(username='test-1')
        self.g1, created = Group.objects.get_or_create(name='test-group-1')

        # Request
        self.req1 = RequestFactory().get('/role-included1/view_by_role/')
        self.req1.user = self.u1

        # Session
        middleware = SessionMiddleware()
        middleware.process_request(self.req1)
        self.req1.session.save()

        # ViewAccess
        self.view_access, created = ViewAccess.objects.get_or_create(
            view='roles:view_protected_by_role')

    def fixture_role(self, user, view_access):
        user.groups.add(self.g1)
        user.save()
        view_access.roles.add(self.g1)
        view_access.save()

    def test_secured_view_as_public_with_no_authorization_and_no_role(self):
        self.view_access.type = 'pu'
        self.view_access.save()
        logout(self.req1)
        self.assertTrue(get_view_access(self.req1.user, 'roles',
                                        'view_protected_by_role'))

    def test_secured_view_as_public_with_authorization_and_no_role(self):
        self.view_access.type = 'pu'
        self.view_access.save()
        login(self.req1, self.u1)
        self.assertTrue(get_view_access(self.req1.user, 'roles',
                                        'view_protected_by_role'))

    def test_secured_view_as_public_with_no_authorization_and_role(self):
        self.view_access.type = 'pu'
        self.view_access.save()
        logout(self.req1)
        self.assertTrue(get_view_access(self.req1.user, 'roles',
                                        'view_protected_by_role'))

    def test_secured_view_as_public_with_authorization_and_role(self):
        self.view_access.type = 'pu'
        self.view_access.save()
        self.fixture_role(self.u1, self.view_access)
        login(self.req1, self.u1)
        self.assertTrue(get_view_access(self.req1.user, 'roles',
                                        'view_protected_by_role'))

    def test_secured_view_as_authorized_with_no_authorization_and_no_role(self):
        self.view_access.type = 'au'
        self.view_access.save()
        logout(self.req1)
        with self.assertRaises(PermissionDenied):
            get_view_access(self.req1.user, 'roles', 'view_protected_by_role')

    def test_secured_view_as_authorized_with_authorization_and_no_role(self):
        self.view_access.type = 'au'
        self.view_access.save()
        login(self.req1, self.u1)
        self.assertTrue(get_view_access(self.req1.user, 'roles',
                                        'view_protected_by_role'))

    def test_secured_view_as_authorized_with_no_authorization_and_role(self):
        self.view_access.type = 'au'
        self.view_access.save()
        self.fixture_role(self.u1, self.view_access)
        logout(self.req1)
        with self.assertRaises(PermissionDenied):
            get_view_access(self.req1.user, 'roles', 'view_protected_by_role')

    def test_secured_view_as_authorized_with_authorization_and_role(self):
        self.view_access.type = 'au'
        self.view_access.save()
        self.fixture_role(self.u1, self.view_access)
        login(self.req1, self.u1)
        self.assertTrue(get_view_access(self.req1.user, 'roles',
                                        'view_protected_by_role'))

    def test_secured_view_by_role_with_no_authorization_and_no_role(self):
        self.view_access.type = 'br'
        self.view_access.save()
        self.view_access.roles.add(self.g1)
        self.view_access.save()
        logout(self.req1)
        with self.assertRaises(PermissionDenied):
            get_view_access(self.req1.user, 'roles', 'view_protected_by_role')

    def test_secured_view_by_role_with_authorization_and_no_role(self):
        self.view_access.type = 'br'
        self.view_access.save()
        self.view_access.roles.add(self.g1)
        self.view_access.save()
        self.u1.groups.clear()
        self.u1.save()
        logout(self.req1)
        login(self.req1, self.u1)
        with self.assertRaises(PermissionDenied):
            get_view_access(self.req1.user, 'roles', 'view_protected_by_role')

    def test_secured_view_by_role_with_no_authorization_and_role(self):
        self.view_access.type = 'br'
        self.view_access.save()
        self.fixture_role(self.u1, self.view_access)
        logout(self.req1)
        with self.assertRaises(PermissionDenied):
            get_view_access(self.req1.user, 'roles', 'view_protected_by_role')

    def test_secured_view_by_role_with_authorization_and_role(self):
        self.view_access.type = 'br'
        self.view_access.save()
        self.fixture_role(self.u1, self.view_access)
        login(self.req1, self.u1)
        self.assertTrue(get_view_access(self.req1.user, 'roles',
                                        'view_protected_by_role'))


class GetInstalledAppTest(unittest.TestCase):
    """
    """

    def test_get_dictionary_with_settings_variables_all_Nones(self):
        """
        """
        expected_dictionary = {
            'NOT_SECURED': [],
            'PUBLIC': [],
            'SECURED': [],
        }
        settings_dictionary = get_setting_dictionary()
        self.assertEqual(expected_dictionary, settings_dictionary)

    def test_get_dictionary_with_settings_variables_SECURED(self):
        """
        """
        settings.__setattr__('SECURED', ['one_application'])
        expected_dictionary = {
            'NOT_SECURED': [],
            'PUBLIC': [],
            'SECURED': ['one_application'],
        }
        settings_dictionary = get_setting_dictionary()
        # Clear mock value to not interfere with other tests
        settings.__delattr__('SECURED')
        self.assertEqual(expected_dictionary, settings_dictionary)

    def test_get_dictionary_with_settings_variables_NOT_SECURED(self):
        """
        """
        settings.__setattr__('NOT_SECURED', ['two_application'])
        expected_dictionary = {
            'NOT_SECURED': ['two_application'],
            'PUBLIC': [],
            'SECURED': [],
        }
        settings_dictionary = get_setting_dictionary()
        # Clear mock value to not interfere with other tests
        settings.__delattr__('NOT_SECURED')
        self.assertEqual(expected_dictionary, settings_dictionary)

    def test_get_dictionary_with_settings_variables_PUBLIC(self):
        """
        """
        settings.__setattr__('PUBLIC', ['last_application'])
        expected_dictionary = {
            'NOT_SECURED': [],
            'PUBLIC': ['last_application'],
            'SECURED': [],
        }
        settings_dictionary = get_setting_dictionary()
        # Clear mock value to not interfere with other tests
        settings.__delattr__('PUBLIC')
        self.assertEqual(expected_dictionary, settings_dictionary)

    def test_get_dictionary_with_settings_variables_with_combination(self):
        """
        """
        settings.__setattr__('PUBLIC', ['last_application'])
        settings.__setattr__('SECURED', ['one_application'])
        expected_dictionary = {
            'NOT_SECURED': [],
            'PUBLIC': ['last_application'],
            'SECURED': ['one_application'],
        }
        settings_dictionary = get_setting_dictionary()
        # Clear mock value to not interfere with other tests
        settings.__delattr__('PUBLIC')
        settings.__delattr__('SECURED')
        self.assertEqual(expected_dictionary, settings_dictionary)


@modify_settings(INSTALLED_APPS={
    'append': 'roles'
})
@override_settings(ROOT_URLCONF='tests.urls')
class TestCheckAccessByRoleWithSecuredApplications(TestCase):

    def setUp(self):
        settings.__setattr__('SECURED', ['roles'])
        # User
        self.u1, created = User.objects.get_or_create(username='test-1')

        # Request
        self.req1 = RequestFactory().get('/role-included1/view_by_role/')
        self.req1.user = self.u1

        # Session
        middleware = SessionMiddleware()
        middleware.process_request(self.req1)
        self.req1.session.save()

    def tearDown(self):
        settings.__delattr__('SECURED')

    def test_not_authorized_user_can_not_access(self):
        """
        By default SECURED applications require *authorized* access if there
        is no ViewAccess created for the view.
        """
        logout(self.req1)
        assert not check_access_by_role(self.req1)

    def test_authorized_user_can_access_views_without_configuration(self):
        """
        User is authorized, should be able to access views without ViewAccess
        created when is a SECURED application.
        :return:
        """
        login(self.req1, self.u1)
        assert check_access_by_role(self.req1)


@modify_settings(INSTALLED_APPS={
    'append': 'roles'
})
@override_settings(ROOT_URLCONF='tests.urls')
class TestCheckAccessByRoleWithPublicApplications(TestCase):

    def setUp(self):
        settings.__setattr__('PUBLIC', ['roles'])
        # User and group
        self.u1, created = User.objects.get_or_create(username='test-1')
        self.g1, created = Group.objects.get_or_create(name='test-group-1')

        # Request
        self.req1 = RequestFactory().get('/role-included1/view_by_role/')
        self.req1.user = self.u1

        # Session
        middleware = SessionMiddleware()
        middleware.process_request(self.req1)
        self.req1.session.save()

    def tearDown(self):
        settings.__delattr__('PUBLIC')

    def fixture_role(self, user, view_access):
        user.groups.add(self.g1)
        user.save()
        view_access.roles.add(self.g1)
        view_access.save()

    def test_not_authenticated_user_can_access(self):
        logout(self.req1)
        assert check_access_by_role(self.req1)

    def test_authorized_user_can_access(self):
        login(self.req1, self.u1)
        assert check_access_by_role(self.req1)


@modify_settings(INSTALLED_APPS={
    'append': 'roles'
})
@override_settings(ROOT_URLCONF='tests.urls')
class TestCheckAccessByRoleWithNotSecuredApplications(TestCase):
    """
    NOT_SECURED applications should not be taken in consideration.
    """

    def setUp(self):
        settings.__setattr__('NOT_SECURED', ['roles'])
        # User and group
        self.u1, created = User.objects.get_or_create(username='test-1')
        self.g1, created = Group.objects.get_or_create(name='test-group-1')

        # Request
        self.req1 = RequestFactory().get('/role-included1/view_by_role/')
        self.req1.user = self.u1

        # Session
        middleware = SessionMiddleware()
        middleware.process_request(self.req1)
        self.req1.session.save()

    def tearDown(self):
        settings.__delattr__('NOT_SECURED')

    def test_not_secured_app_views_are_ignored_without_authentication(self):
        """
        Despite NOT SECURED applications should be applications without any view
        the test will verify NOT SECURED application are really ignored.
        """
        logout(self.req1)
        assert check_access_by_role(self.req1)

    def test_not_secured_app_views_are_ignored_with_authentication(self):
        """
        Despite NOT SECURED applications should be applications without any view
        the test will verify NOT SECURED application are really ignored.
        """
        login(self.req1, self.u1)
        assert check_access_by_role(self.req1)

    def test_not_secured_app_views_have_no_precedence_against_ViewAccess(self):
        """
        Despite NOT SECURED applications should be applications without any view
        the test will verify that if exist a ViewAccess for the view being
        request by the user, this will be ignored.
        """
        ViewAccess.objects.get_or_create(
            view='roles:view_protected_by_role',
            type='au')
        logout(self.req1)
        assert check_access_by_role(self.req1)


@modify_settings(INSTALLED_APPS={
    'append': 'roles'
})
@override_settings(ROOT_URLCONF='tests.urls')
class TestCheckAccessByRoleWithoutAnySettings(TestCase):

    def setUp(self):
        # User and group
        self.u1, created = User.objects.get_or_create(username='test-1')
        self.g1, created = Group.objects.get_or_create(name='test-group-1')

        # Request
        self.req1 = RequestFactory().get('/role-included1/view_by_role/')
        self.req1.user = self.u1

        # Session
        middleware = SessionMiddleware()
        middleware.process_request(self.req1)
        self.req1.session.save()

    def test_any_user_with_authentication_can_access(self):
        login(self.req1, self.u1)
        assert check_access_by_role(self.req1)

    def test_any_user_without_authentication_can_access(self):
        logout(self.req1)
        assert check_access_by_role(self.req1)

    def test_ViewAccess_take_precedence_over_no_configuration_no_login(self):
        ViewAccess.objects.get_or_create(
            view='roles:view_protected_by_role',
            type='au')
        logout(self.req1)
        with self.assertRaises(PermissionDenied):
            check_access_by_role(self.req1)

    def test_ViewAccess_take_precedence_over_no_configuration_with_login(self):
        ViewAccess.objects.get_or_create(
            view='roles:view_protected_by_role',
            type='au')
        login(self.req1, self.u1)
        assert check_access_by_role(self.req1)

    def test_ViewAccess_denied_access_if_no_role(self):
        view_access, created = ViewAccess.objects.get_or_create(
            view='roles:view_protected_by_role',
            type='br')
        view_access.roles.add(self.g1)

        login(self.req1, self.u1)
        with self.assertRaises(PermissionDenied):
            check_access_by_role(self.req1)

    def test_ViewAccess_grant_access_if_role(self):
        view_access, created = ViewAccess.objects.get_or_create(
            view='roles:view_protected_by_role',
            type='br')
        view_access.roles.add(self.g1)
        view_access.save()
        self.u1.groups.add(self.g1)
        self.u1.save()

        login(self.req1, self.u1)
        assert check_access_by_role(self.req1)
