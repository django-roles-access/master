from unittest import TestCase as UnitTestCase
import pytest
from django.conf import settings
from django.contrib.auth import logout, login
from django.contrib.auth.models import User, Group
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory, TestCase
try:
    from unittest.mock import Mock, patch
except:
    from mock import Mock, patch

from django_roles.models import ViewAccess
from django_roles.tools import (get_setting_dictionary, get_view_access,
                                check_access_by_role, get_app_type)


@patch('django_roles.tools.resolve')
@patch('django_roles.tools.ViewAccess.objects')
class UnitTestGetViewAccess(UnitTestCase):

    def setUp(self):
        self.request = Mock()
        self.request.user = Mock()

    def test_secured_view_as_public_with_no_authorization_and_no_role(
            self, mock_objects, mock_resolve
    ):
        view_access = Mock()
        view_access.type = 'pu'
        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = view_access
        assert get_view_access(self.request)

    def test_secured_view_as_authorized_user_is_authenticated(
            self, mock_objects, mock_resolve
    ):
        view_access = Mock()
        view_access.type = 'au'
        self.request.user.is_authenticated = True
        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = view_access
        assert get_view_access(self.request)

    def test_secured_view_as_authorized_user_is_not_authenticated(
            self, mock_objects, mock_resolve
    ):
        view_access = Mock()
        view_access.type = 'au'
        self.request.user.is_authenticated = False
        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = view_access
        with self.assertRaises(PermissionDenied):
            get_view_access(self.request)

    def test_secured_view_by_role_user_is_not_authenticated(
            self, mock_objects, mock_resolve
    ):
        view_access = Mock()
        view_access.type = 'br'
        self.request.user.is_authenticated = False
        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = view_access
        with self.assertRaises(PermissionDenied):
            get_view_access(self.request)

    def test_secured_view_by_role_user_is_not_authenticated_not_in_group(
            self, mock_objects, mock_resolve
    ):
        view_access = Mock()
        view_access.type = 'br'
        view_access.roles.all.return_value = ['need-access', 'fake-access']
        self.request.user.is_authenticated = True
        self.request.user.groups.all.return_value = []
        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = view_access
        with self.assertRaises(PermissionDenied):
            get_view_access(self.request)

    def test_secured_view_by_role_user_is_authenticated_and_in_group(
            self, mock_objects, mock_resolve
    ):
        view_access = Mock()
        view_access.type = 'br'
        view_access.roles.all.return_value = ['need-access', 'fake-access']
        self.request.user.is_authenticated = True
        self.request.user.groups.all.return_value = ['fake-access']
        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = view_access
        get_view_access(self.request)


@pytest.mark.django_db
class TestGetViewAccess(UnitTestCase):

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
            view='django_roles:view_protected_by_role',
            type='pu'
        )

    def fixture_role(self, user, view_access):
        user.groups.add(self.g1)
        user.save()
        view_access.roles.add(self.g1)
        view_access.save()

    def test_secured_view_as_public_with_no_authorization_and_no_role(self):
        self.view_access.type = 'pu'
        self.view_access.save()
        logout(self.req1)
        self.assertTrue(get_view_access(self.req1))

    def test_secured_view_as_public_with_authorization_and_no_role(self):
        self.view_access.type = 'pu'
        self.view_access.save()
        login(self.req1, self.u1)
        self.assertTrue(get_view_access(self.req1))

    def test_secured_view_as_public_with_no_authorization_and_role(self):
        self.view_access.type = 'pu'
        self.view_access.save()
        logout(self.req1)
        self.assertTrue(get_view_access(self.req1))

    def test_secured_view_as_public_with_authorization_and_role(self):
        self.view_access.type = 'pu'
        self.view_access.save()
        self.fixture_role(self.u1, self.view_access)
        login(self.req1, self.u1)
        self.assertTrue(get_view_access(self.req1))

    def test_secured_view_as_authorized_with_no_authorization_and_no_role(self):
        self.view_access.type = 'au'
        self.view_access.save()
        logout(self.req1)
        with self.assertRaises(PermissionDenied):
            get_view_access(self.req1)

    def test_secured_view_as_authorized_with_authorization_and_no_role(self):
        self.view_access.type = 'au'
        self.view_access.save()
        login(self.req1, self.u1)
        self.assertTrue(get_view_access(self.req1))

    def test_secured_view_as_authorized_with_no_authorization_and_role(self):
        self.view_access.type = 'au'
        self.view_access.save()
        self.fixture_role(self.u1, self.view_access)
        logout(self.req1)
        with self.assertRaises(PermissionDenied):
            get_view_access(self.req1)

    def test_secured_view_as_authorized_with_authorization_and_role(self):
        self.view_access.type = 'au'
        self.view_access.save()
        self.fixture_role(self.u1, self.view_access)
        login(self.req1, self.u1)
        self.assertTrue(get_view_access(self.req1))

    def test_secured_view_by_role_with_no_authorization_and_no_role(self):
        self.view_access.type = 'br'
        self.view_access.save()
        self.view_access.roles.add(self.g1)
        self.view_access.save()
        logout(self.req1)
        with self.assertRaises(PermissionDenied):
            get_view_access(self.req1)

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
            get_view_access(self.req1)

    def test_secured_view_by_role_with_no_authorization_and_role(self):
        self.view_access.type = 'br'
        self.view_access.save()
        self.fixture_role(self.u1, self.view_access)
        logout(self.req1)
        with self.assertRaises(PermissionDenied):
            get_view_access(self.req1)

    def test_secured_view_by_role_with_authorization_and_role(self):
        self.view_access.type = 'br'
        self.view_access.save()
        self.fixture_role(self.u1, self.view_access)
        login(self.req1, self.u1)
        self.assertTrue(get_view_access(self.req1))


@pytest.mark.django_db
class TestGetViewAccessWithDirectView(UnitTestCase):

    def setUp(self):
        # User and group
        self.u1, created = User.objects.get_or_create(username='test-1')
        self.g1, created = Group.objects.get_or_create(name='test-group-1')

        # Request
        self.req1 = RequestFactory().get('/direct_access_view/')
        self.req1.user = self.u1

        # Session
        middleware = SessionMiddleware()
        middleware.process_request(self.req1)
        self.req1.session.save()

        # ViewAccess
        self.view_access, created = ViewAccess.objects.get_or_create(
            view='direct_access_view',
            type='au'
        )

    def test_secured_view_without_app_name_with_authentication(self):
        login(self.req1, self.u1)
        self.assertTrue(get_view_access(self.req1))

    def test_secured_view_without_app_name_without_authentication(self):
        logout(self.req1)
        with self.assertRaises(PermissionDenied):
            get_view_access(self.req1)


@pytest.mark.django_db
class TestNestedNameSpaces(UnitTestCase):

    def setUp(self):
        # User and group
        self.u1, created = User.objects.get_or_create(username='test-1')
        self.g1, created = Group.objects.get_or_create(name='test-group-1')

        # Request
        self.req1 = RequestFactory().get(
            '/nest1/nest2/view_by_role/')
        self.req1.user = self.u1

        # Session
        middleware = SessionMiddleware()
        middleware.process_request(self.req1)
        self.req1.session.save()

        # ViewAccess
        self.view_access, created = ViewAccess.objects.get_or_create(
            view='nest1_namespace:nest2_namespace:view_protected_by_role',
            type='au'
        )

    def test_secured_view_with_nested_namespace(self):
        login(self.req1, self.u1)
        self.assertTrue(get_view_access(self.req1))

    def test_secured_view_without_nested_namespace_without_authentication(self):
        logout(self.req1)
        with self.assertRaises(PermissionDenied):
            get_view_access(self.req1)

    def test_check_secured_view_with_nested_namespace(self):
        login(self.req1, self.u1)
        self.assertTrue(check_access_by_role(self.req1))

    def test_check_secured_view_without_nested_namespace_without_authentication(
            self):
        logout(self.req1)
        with self.assertRaises(PermissionDenied):
            check_access_by_role(self.req1)


class TestGetDictionarySettings(UnitTestCase):
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


@patch('django_roles.tools.resolve')
@patch('django_roles.tools.get_view_access')
class TestCheckAccessByRole(UnitTestCase):

    def setUp(self):
        self.request = Mock()

    @patch('django_roles.tools.get_setting_dictionary')
    def test_get_setting_dictionary_is_called(
            self, mock_get_setting_dctionary, mock_get_view_access, mock_resolve
    ):
        check_access_by_role(self.request)
        mock_get_setting_dctionary.assert_called()

    @patch('django_roles.tools.get_setting_dictionary')
    def test_get_setting_dictionary_is_called_once(
            self, mock_get_setting_dctionary, mock_get_view_access, mock_resolve
    ):
        check_access_by_role(self.request)
        mock_get_setting_dctionary.assert_called_once()

    def test_get_view_access_is_called(
            self, mock_get_view_access, mock_resolve
    ):
        check_access_by_role(self.request)
        mock_get_view_access.assert_called()

    def test_get_view_access_is_called_once(
            self, mock_get_view_access, mock_resolve
    ):
        check_access_by_role(self.request)
        mock_get_view_access.assert_called_once()

    def test_get_view_access_is_called_with(
            self, mock_get_view_access, mock_resolve
    ):
        self.request.user = Mock()
        check_access_by_role(self.request)
        mock_get_view_access.assert_called_once_with(
            self.request
        )


# Integrated tests
class TestCheckAccessByRoleWithSecuredApplications(TestCase):

    def setUp(self):
        settings.__setattr__('SECURED', ['django_roles'])
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


class TestCheckAccessByRoleWithPublicApplications(TestCase):

    def setUp(self):
        settings.__setattr__('PUBLIC', ['django_roles'])
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


class TestCheckAccessByRoleWithNotSecuredApplications(TestCase):
    """
    NOT_SECURED applications should not be taken in consideration.
    """

    def setUp(self):
        settings.__setattr__('NOT_SECURED', ['django_roles'])
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
            view='django_roles:view_protected_by_role',
            type='au')
        logout(self.req1)
        assert check_access_by_role(self.req1)


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
            view='django_roles:view_protected_by_role',
            type='au')
        logout(self.req1)
        with self.assertRaises(PermissionDenied):
            check_access_by_role(self.req1)

    def test_ViewAccess_take_precedence_over_no_configuration_with_login(self):
        ViewAccess.objects.get_or_create(
            view='django_roles:view_protected_by_role',
            type='au')
        login(self.req1, self.u1)
        # import pdb
        # pdb.set_trace()
        assert check_access_by_role(self.req1)

    def test_ViewAccess_denied_access_if_no_role(self):
        view_access, created = ViewAccess.objects.get_or_create(
            view='django_roles:view_protected_by_role',
            type='br')
        view_access.roles.add(self.g1)

        login(self.req1, self.u1)
        with self.assertRaises(PermissionDenied):
            check_access_by_role(self.req1)

    def test_ViewAccess_grant_access_if_role(self):
        view_access, created = ViewAccess.objects.get_or_create(
            view='django_roles:view_protected_by_role',
            type='br')
        view_access.roles.add(self.g1)
        view_access.save()
        self.u1.groups.add(self.g1)
        self.u1.save()

        login(self.req1, self.u1)
        assert check_access_by_role(self.req1)


class UnitTestGetAppType(UnitTestCase):

    def test_detect_app_has_no_type(self):
        """
        When no configuration is given, or default case.
        """
        result = get_app_type('fake-app')
        self.assertEqual(result, None)

    @patch('django_roles.tools.get_setting_dictionary')
    def test_get_settings_dictionary_is_called(
            self, mock_get_settings_dictionary
    ):
        get_app_type('fake-app')
        mock_get_settings_dictionary.assert_called()

    @patch('django_roles.tools.get_setting_dictionary')
    def test_get_settings_dictionary_is_called_once(
            self, mock_get_settings_dictionary
    ):
        mock_get_settings_dictionary.return_value = {'type 1': [],
                                                     'type 2': []}
        get_app_type('fake-app')
        mock_get_settings_dictionary.assert_called_once()

    @patch('django_roles.tools.get_setting_dictionary')
    def test_get_settings_dictionary_is_called_once_with_no_param(
            self, mock_get_settings_dictionary
    ):
        get_app_type('fake-app')
        mock_get_settings_dictionary.assert_called_once_with()

    @patch('django_roles.tools.get_setting_dictionary')
    def test_detect_app_is_any_configured_type(
            self, mock_get_settings_dictionary
    ):
        _dict = {
            'type 1': ['blue', 'red'],
            'any type': ['orange', 'fake-app', 'sky']
        }
        mock_get_settings_dictionary.return_value = _dict
        result = get_app_type('fake-app')
        expected = u'any type'
        self.assertEqual(result, expected)


class IntegratedTestGetAppType(UnitTestCase):

    def setUp(self):
        settings.__setattr__('NOT_SECURED', ['not_secured_app'])
        settings.__setattr__('PUBLIC', ['public_app'])
        settings.__setattr__('SECURED', ['secured_app'])

    def tearDown(self):
        settings.__delattr__('NOT_SECURED')
        settings.__delattr__('PUBLIC')
        settings.__delattr__('SECURED')

    def test_default_case_with_no_configuration(self):
        result = get_app_type('app_name')
        self.assertIs(result, None)

    def test_detect_NOT_SECURED_configured_app(self):
        result = get_app_type('not_secured_app')
        expected = 'NOT_SECURED'
        self.assertEqual(result, expected)

    def test_detect_PUBLIC_configured_app(self):
        result = get_app_type('public_app')
        expected = 'PUBLIC'
        self.assertEqual(result, expected)

    def test_detect_SECURED_configured_app(self):
        result = get_app_type('secured_app')
        expected = 'SECURED'
        self.assertEqual(result, expected)
