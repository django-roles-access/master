from unittest import TestCase as UnitTestCase
import pytest
from django.conf import settings
from django.contrib.auth import logout, login
from django.contrib.auth.models import User, Group
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.test import RequestFactory, TestCase
try:
    from unittest.mock import Mock, patch
except:
    from mock import Mock, patch

from django_roles_access.models import ViewAccess
from django_roles_access.tools import (get_setting_dictionary, get_view_access,
                                       check_access_by_role, get_app_type,
                                       get_forbidden_message,
                                       DEFAULT_FORBIDDEN_MESSAGE,
                                       get_no_access_response)


@patch('django_roles_access.tools.resolve')
@patch('django_roles_access.tools.ViewAccess.objects')
class UnitTestGetViewAccess(UnitTestCase):

    def setUp(self):
        self.request = Mock()
        self.request.user = Mock()

    def test_filter_is_done_with_view_name(
            self, mock_objects, mock_resolve
    ):
        used_url = Mock()
        used_url.view_name = 'fake-namespace:fake-view-name'
        mock_resolve.return_value = used_url

        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = Mock()
        get_view_access(self.request)
        mock_objects.filter.assert_called_with(
            view='fake-namespace:fake-view-name')

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
        assert not get_view_access(self.request)

    def test_secured_view_by_role_user_is_not_authenticated(
            self, mock_objects, mock_resolve
    ):
        view_access = Mock()
        view_access.type = 'br'
        self.request.user.is_authenticated = False
        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = view_access
        assert not get_view_access(self.request)

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
        assert not get_view_access(self.request)

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
        assert get_view_access(self.request)
        # self.fail(u'Finish this???')

    def test_get_view_access_return_None_in_no_view_access_object(
            self, mock_objects, mock_resolve
    ):
        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = None
        self.assertEqual(get_view_access(self.request), None)


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
            view='django_roles_access:view_protected_by_role',
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
        assert get_view_access(self.req1)

    def test_secured_view_as_public_with_authorization_and_no_role(self):
        self.view_access.type = 'pu'
        self.view_access.save()
        login(self.req1, self.u1)
        assert get_view_access(self.req1)

    def test_secured_view_as_public_with_no_authorization_and_role(self):
        self.view_access.type = 'pu'
        self.view_access.save()
        logout(self.req1)
        assert get_view_access(self.req1)

    def test_secured_view_as_public_with_authorization_and_role(self):
        self.view_access.type = 'pu'
        self.view_access.save()
        self.fixture_role(self.u1, self.view_access)
        login(self.req1, self.u1)
        assert get_view_access(self.req1)

    def test_secured_view_as_authorized_with_no_authorization_and_no_role(self):
        self.view_access.type = 'au'
        self.view_access.save()
        logout(self.req1)
        assert not get_view_access(self.req1)

    def test_secured_view_as_authorized_with_authorization_and_no_role(self):
        self.view_access.type = 'au'
        self.view_access.save()
        login(self.req1, self.u1)
        assert get_view_access(self.req1)

    def test_secured_view_as_authorized_with_no_authorization_and_role(self):
        self.view_access.type = 'au'
        self.view_access.save()
        self.fixture_role(self.u1, self.view_access)
        logout(self.req1)
        assert not get_view_access(self.req1)

    def test_secured_view_as_authorized_with_authorization_and_role(self):
        self.view_access.type = 'au'
        self.view_access.save()
        self.fixture_role(self.u1, self.view_access)
        login(self.req1, self.u1)
        assert get_view_access(self.req1)

    def test_secured_view_by_role_with_no_authorization_and_no_role(self):
        self.view_access.type = 'br'
        self.view_access.save()
        self.view_access.roles.add(self.g1)
        self.view_access.save()
        logout(self.req1)
        assert not get_view_access(self.req1)

    def test_secured_view_by_role_with_authorization_and_no_role(self):
        self.view_access.type = 'br'
        self.view_access.save()
        self.view_access.roles.add(self.g1)
        self.view_access.save()
        self.u1.groups.clear()
        self.u1.save()
        logout(self.req1)
        login(self.req1, self.u1)
        assert not get_view_access(self.req1)

    def test_secured_view_by_role_with_no_authorization_and_role(self):
        self.view_access.type = 'br'
        self.view_access.save()
        self.fixture_role(self.u1, self.view_access)
        logout(self.req1)
        assert not get_view_access(self.req1)

    def test_secured_view_by_role_with_authorization_and_role(self):
        self.view_access.type = 'br'
        self.view_access.save()
        self.fixture_role(self.u1, self.view_access)
        login(self.req1, self.u1)
        assert get_view_access(self.req1)


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
        assert not get_view_access(self.req1)


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
        assert not get_view_access(self.req1)

    def test_check_secured_view_without_nested_namespace_without_authentication(
            self):
        view_access, created = ViewAccess.objects.get_or_create(
            view='direct_access_view',
            type='au'
        )
        request = RequestFactory().get('/direct_access_view/')
        request.user = self.u1
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        logout(request)
        assert not check_access_by_role(request)


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
            'DISABLED': [],
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
            'DISABLED': [],
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
            'DISABLED': [],
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
            'DISABLED': [],
        }
        settings_dictionary = get_setting_dictionary()
        # Clear mock value to not interfere with other tests
        settings.__delattr__('PUBLIC')
        self.assertEqual(expected_dictionary, settings_dictionary)

    def test_get_dictionary_with_settings_variables_DISABLED(self):
        """
        """
        settings.__setattr__('DISABLED', ['disabled_application'])
        expected_dictionary = {
            'NOT_SECURED': [],
            'PUBLIC': [],
            'SECURED': [],
            'DISABLED': ['disabled_application'],
        }
        settings_dictionary = get_setting_dictionary()
        # Clear mock value to not interfere with other tests
        settings.__delattr__('DISABLED')
        self.assertEqual(expected_dictionary, settings_dictionary)

    def test_get_dictionary_with_settings_variables_with_combination(self):
        """
        """
        settings.__setattr__('PUBLIC', ['last_application'])
        settings.__setattr__('SECURED', ['one_application'])
        settings.__setattr__('DISABLED', ['disabled_application'])
        expected_dictionary = {
            'NOT_SECURED': [],
            'PUBLIC': ['last_application'],
            'SECURED': ['one_application'],
            'DISABLED': ['disabled_application'],
        }
        settings_dictionary = get_setting_dictionary()
        # Clear mock value to not interfere with other tests
        settings.__delattr__('PUBLIC')
        settings.__delattr__('SECURED')
        settings.__delattr__('DISABLED')
        self.assertEqual(expected_dictionary, settings_dictionary)


@patch('django_roles_access.tools.resolve')
@patch('django_roles_access.tools.get_view_access')
class UnitTestCheckAccessByRole(UnitTestCase):

    def setUp(self):
        self.request = Mock()

    def test_resolve_called_with_request_path_info(
            self, mock_get_view_access, mock_resolve
    ):
        check_access_by_role(self.request)
        mock_resolve.assert_called_once_with(self.request.path_info)

    @patch('django_roles_access.tools.get_setting_dictionary')
    def test_get_setting_dictionary_is_called(
            self, mock_get_setting_dictionary, mock_get_view_access,
            mock_resolve
    ):
        check_access_by_role(self.request)
        assert mock_get_setting_dictionary.called

    @patch('django_roles_access.tools.get_setting_dictionary')
    def test_get_setting_dictionary_is_called_once(
            self, mock_get_setting_dictionary, mock_get_view_access,
            mock_resolve
    ):
        check_access_by_role(self.request)
        self.assertEqual(mock_get_setting_dictionary.call_count, 1)

    @patch('django_roles_access.tools.get_setting_dictionary')
    def test_app_name_is_searched_as_NOT_SECURED_before_get_view_access(
            self, mock_get_setting_dictionary, mock_get_view_access,
            mock_resolve
    ):
        """
        Default behavior of NOT_SECURED applications is not to check access.
        """
        used_url = Mock()
        used_url.app_name = 'fake-app-name'
        mock_resolve.return_value = used_url
        mock_get_setting_dictionary.return_value = {
            'NOT_SECURED': ['fake-app-name']
        }
        assert check_access_by_role(self.request)
        assert not mock_get_view_access.called

    def test_get_view_access_is_called(
            self, mock_get_view_access, mock_resolve
    ):
        check_access_by_role(self.request)
        assert mock_get_view_access.called

    def test_get_view_access_is_called_once(
            self, mock_get_view_access, mock_resolve
    ):
        check_access_by_role(self.request)
        self.assertEqual(mock_get_view_access.call_count, 1)

    def test_get_view_access_is_called_with(
            self, mock_get_view_access, mock_resolve
    ):
        self.request.user = Mock()
        check_access_by_role(self.request)
        mock_get_view_access.assert_called_once_with(
            self.request
        )

    @patch('django_roles_access.tools.get_setting_dictionary')
    def test_get_view_access_take_precedence_over_default_behavior(
            self, mock_get_setting_dictionary, mock_get_view_access,
            mock_resolve
    ):
        """
        If a ViewAccess object exist for the view, this must be first than
        default behaviors.
        """
        used_url = Mock()
        used_url.app_name = 'fake-app-name'
        mock_resolve.return_value = used_url
        mock_get_setting_dictionary.return_value = {
            'NOT_SECURED': [],
            'PUBLIC': [],
            'SECURED': ['fake-app-name'],
            'DISABLED': []
        }
        mock_get_view_access.return_value = True
        self.request.user.is_authenticated = False
        assert check_access_by_role(self.request)

    @patch('django_roles_access.tools.get_setting_dictionary')
    def test_default_PUBLIC_behavior(
            self, mock_get_setting_dictionary, mock_get_view_access,
            mock_resolve
    ):
        used_url = Mock()
        used_url.app_name = 'fake-app-name'
        mock_resolve.return_value = used_url
        mock_get_setting_dictionary.return_value = {
            'NOT_SECURED': [],
            'PUBLIC': ['fake-app-name'],
            'SECURED': [],
            'DISABLED': []
        }
        mock_get_view_access.return_value = None
        assert check_access_by_role(self.request)

    @patch('django_roles_access.tools.get_setting_dictionary')
    def test_default_SECURED_behavior_when_user_not_authenticated(
            self, mock_get_setting_dictionary, mock_get_view_access,
            mock_resolve
    ):
        used_url = Mock()
        used_url.app_name = 'fake-app-name'
        mock_resolve.return_value = used_url
        mock_get_setting_dictionary.return_value = {
            'NOT_SECURED': [],
            'PUBLIC': [],
            'SECURED': ['fake-app-name'],
            'DISABLED': []
        }
        mock_get_view_access.return_value = False
        self.request.user.is_authenticated = False
        assert not check_access_by_role(self.request)

    @patch('django_roles_access.tools.get_setting_dictionary')
    def test_default_SECURED_behavior_when_user_authenticated(
            self, mock_get_setting_dictionary, mock_get_view_access,
            mock_resolve
    ):
        used_url = Mock()
        used_url.app_name = 'fake-app-name'
        mock_resolve.return_value = used_url
        mock_get_setting_dictionary.return_value = {
            'NOT_SECURED': [],
            'PUBLIC': [],
            'SECURED': ['fake-app-name'],
            'DISABLED': []
        }
        mock_get_view_access.return_value = None
        self.request.user.is_authenticated = True
        assert check_access_by_role(self.request)

    @patch('django_roles_access.tools.get_setting_dictionary')
    def test_default_DISABLED_behavior(
            self, mock_get_setting_dictionary, mock_get_view_access,
            mock_resolve
    ):
        used_url = Mock()
        used_url.app_name = 'fake-app-name'
        mock_resolve.return_value = used_url
        mock_get_setting_dictionary.return_value = {
            'NOT_SECURED': [],
            'PUBLIC': [],
            'SECURED': [],
            'DISABLED': ['fake-app-name']
        }
        mock_get_view_access.return_value = None
        assert not check_access_by_role(self.request)

    @patch('django_roles_access.tools.get_setting_dictionary')
    def test_check_access_by_role_return_True_if_any_happen(
            self, mock_get_setting_dictionary, mock_get_view_access,
            mock_resolve
    ):
        """
        In case Django roles is activated, for example with middleware, and
        no more configuration are given, behavior must be: not to change view
        behavior.
        """
        used_url = Mock()
        used_url.app_name = 'fake-app-name'
        mock_resolve.return_value = used_url
        mock_get_setting_dictionary.return_value = {
            'NOT_SECURED': [],
            'PUBLIC': [],
            'SECURED': [],
            'DISABLED': []
        }
        mock_get_view_access.return_value = None
        self.request.user.is_authenticated = False
        assert check_access_by_role(self.request)


# Integrated tests
class TestCheckAccessByRoleWithSecuredApplications(TestCase):

    def setUp(self):
        settings.__setattr__('SECURED', ['django_roles_access'])
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
        settings.__setattr__('PUBLIC', ['django_role_access'])
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
        settings.__setattr__('NOT_SECURED', ['django_roles_access'])
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

    def test_not_secured_app_views_have_precedence_against_ViewAccess(self):
        """
        Despite NOT SECURED applications should be applications without any view
        the test will verify that if exist a ViewAccess for the view being
        request by the user, this will be ignored.
        """
        ViewAccess.objects.get_or_create(
            view='django_roles_access:view_protected_by_role',
            type='au')
        logout(self.req1)
        assert check_access_by_role(self.req1)


class TestCheckAccessByRoleWithDisabledApplications(TestCase):
    """
    NOT_SECURED applications should not be taken in consideration.
    """

    def setUp(self):
        settings.__setattr__('DISABLED', ['django_roles_access'])
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
        settings.__delattr__('DISABLED')

    def test_disabled_app_views_are_forbidden_without_authentication(self):
        """
        Despite NOT SECURED applications should be applications without any view
        the test will verify NOT SECURED application are really ignored.
        """
        logout(self.req1)
        assert not check_access_by_role(self.req1)

    def test_disabled_app_views_are_forbidden_with_authentication(self):
        """
        Despite NOT SECURED applications should be applications without any view
        the test will verify NOT SECURED application are really ignored.
        """
        login(self.req1, self.u1)
        assert not check_access_by_role(self.req1)

    def test_disabled_app_views_have_precedence_against_ViewAccess(self):
        """
        Despite NOT SECURED applications should be applications without any view
        the test will verify that if exist a ViewAccess for the view being
        request by the user, this will be ignored.
        """
        ViewAccess.objects.get_or_create(
            view='django_roles_access:view_protected_by_role',
            type='pu')
        assert not check_access_by_role(self.req1)


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
            view='django_roles_access:view_protected_by_role',
            type='au')
        logout(self.req1)
        assert not check_access_by_role(self.req1)

    def test_ViewAccess_take_precedence_over_no_configuration_with_login(self):
        ViewAccess.objects.get_or_create(
            view='django_roles_access:view_protected_by_role',
            type='au')
        login(self.req1, self.u1)
        # import pdb
        # pdb.set_trace()
        assert check_access_by_role(self.req1)

    def test_ViewAccess_denied_access_if_no_role(self):
        view_access, created = ViewAccess.objects.get_or_create(
            view='django_roles_access:view_protected_by_role',
            type='br')
        view_access.roles.add(self.g1)

        login(self.req1, self.u1)
        assert not check_access_by_role(self.req1)

    def test_ViewAccess_grant_access_if_role(self):
        view_access, created = ViewAccess.objects.get_or_create(
            view='django_roles_access:view_protected_by_role',
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

    @patch('django_roles_access.tools.get_setting_dictionary')
    def test_get_settings_dictionary_is_called(
            self, mock_get_settings_dictionary
    ):
        get_app_type('fake-app')
        assert mock_get_settings_dictionary.called

    @patch('django_roles_access.tools.get_setting_dictionary')
    def test_get_settings_dictionary_is_called_once(
            self, mock_get_settings_dictionary
    ):
        mock_get_settings_dictionary.return_value = {'type 1': [],
                                                     'type 2': []}
        get_app_type('fake-app')
        self.assertEqual(mock_get_settings_dictionary.call_count, 1)

    @patch('django_roles_access.tools.get_setting_dictionary')
    def test_get_settings_dictionary_is_called_once_with_no_param(
            self, mock_get_settings_dictionary
    ):
        get_app_type('fake-app')
        mock_get_settings_dictionary.assert_called_once_with()

    @patch('django_roles_access.tools.get_setting_dictionary')
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


class UnitTestGetForbiddenMessage(UnitTestCase):

    def test_default_forbidden_message(self):
        assert DEFAULT_FORBIDDEN_MESSAGE == get_forbidden_message()

    @patch('django_roles_access.tools.settings')
    def test_forbidden_configured_message(
            self, mock_settings
    ):
        mock_settings.DJANGO_ROLES_ACCESS_FORBIDDEN_MESSAGE = 'fake-message'
        assert 'fake-message' == get_forbidden_message()


class IntegratedTestGetForbiddenMessage(TestCase):

    def test_default_forbidden_message(self):
        assert DEFAULT_FORBIDDEN_MESSAGE == get_forbidden_message()

    def test_forbidden_configured_message(self):
        settings.__setattr__('DJANGO_ROLES_ACCESS_FORBIDDEN_MESSAGE',
                             'forbidden-message')
        response = get_forbidden_message()
        settings.__delattr__('DJANGO_ROLES_ACCESS_FORBIDDEN_MESSAGE')
        assert 'forbidden-message' == response


class UnitTestGetNoAccessResponse(UnitTestCase):

    @patch('django_roles_access.tools.HttpResponseForbidden')
    def test_default_behavior_http_response_forbidden(
            self, mock_http_response_forbidden
    ):
        mock_http_response_forbidden.return_value = 'fake-forbidden'
        response = get_no_access_response()
        assert response == 'fake-forbidden'

    @patch('django_roles_access.tools.HttpResponseForbidden')
    def test_default_behavior_http_response_forbidden_403_Forbidden(
            self, mock_http_response_forbidden
    ):
        argument = u'<h1>403 Forbidden</h1>'
        get_no_access_response()
        mock_http_response_forbidden.assert_called_with(argument)

    @patch('django_roles_access.tools.settings')
    @patch('django_roles_access.tools.HttpResponseForbidden')
    def test_http_response_forbidden_with_configuration(
            self, mock_http_response_forbidden, mock_settings
    ):
        mock_settings.DJANGO_ROLES_ACCESS_REDIRECT = False
        mock_settings.DJANGO_ROLES_ACCESS_FORBIDDEN_MESSAGE = 'fake-message'
        get_no_access_response()
        mock_http_response_forbidden.assert_called_with('fake-message')

    @patch('django_roles_access.tools.settings')
    @patch('django_roles_access.tools.HttpResponseRedirect')
    def test_redirect_if_redirect_is_configured(
            self, mock_http_response_redirect, mock_settings
    ):
        mock_settings.DJANGO_ROLES_ACCESS_REDIRECT = True
        mock_http_response_redirect.return_value = 'fake-redirect'
        response = get_no_access_response()
        assert response == 'fake-redirect'

    @patch('django_roles_access.tools.settings')
    @patch('django_roles_access.tools.HttpResponseRedirect')
    def test_redirect_if_redirect_to_LOGIN_URL(
            self, mock_http_response_redirect, mock_settings
    ):
        mock_settings.DJANGO_ROLES_ACCESS_REDIRECT = True
        mock_settings.LOGIN_URL = 'fake-login'
        get_no_access_response()
        mock_http_response_redirect.assert_called_with('fake-login')


class IntegratedTextGetNoAccessResponse(TestCase):

    def test_default_behavior_http_response_forbidden(self):
        response = get_no_access_response()
        self.assertIsInstance(response, HttpResponseForbidden)

    def test_default_behavior_http_response_forbidden_403_Forbidden(self):
        response = get_no_access_response()
        self.assertIn(DEFAULT_FORBIDDEN_MESSAGE,
                      response.content.decode('utf-8'))

    def test_http_response_forbidden_with_configuration(self):
        settings.__setattr__('DJANGO_ROLES_ACCESS_FORBIDDEN_MESSAGE',
                             'forbidden-message')
        response = get_no_access_response()
        settings.__delattr__('DJANGO_ROLES_ACCESS_FORBIDDEN_MESSAGE')
        self.assertIn('forbidden-message', response.content.decode('utf-8'))

    def test_redirect_if_redirect_is_configured(self):
        settings.__setattr__('DJANGO_ROLES_ACCESS_REDIRECT', True)
        response = get_no_access_response()
        settings.__delattr__('DJANGO_ROLES_ACCESS_REDIRECT')
        self.assertIsInstance(response, HttpResponseRedirect)

    def test_redirect_if_redirect_to_LOGIN_URL(self):
        settings.__setattr__('DJANGO_ROLES_ACCESS_REDIRECT', True)
        response = get_no_access_response()
        settings.__delattr__('DJANGO_ROLES_ACCESS_REDIRECT')
        self.assertEqual(settings.LOGIN_URL, response.url)
