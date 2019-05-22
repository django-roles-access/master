from importlib import import_module
from unittest import TestCase as UnitTestCase

from django.contrib.auth.models import Group
from django.core.management import BaseCommand
from django.conf import settings
from django.test import TestCase
from django.views.generic import TemplateView
try:
    from unittest.mock import Mock, patch, MagicMock
except:
    from mock import Mock, patch

from django_roles_access.decorator import access_by_role
from django_roles_access.mixin import RolesMixin
from django_roles_access.models import ViewAccess
from tests import views
from django_roles_access.utils import (walk_site_url, get_views_by_app,
                                       view_access_analyzer,
                                       get_view_analyze_report,
                                       check_django_roles_is_used,
                                       analyze_by_role, APP_NAME_FOR_NONE,
                                       NOT_SECURED_DEFAULT, SECURED_DEFAULT,
                                       PUBLIC_DEFAULT, NONE_TYPE_DEFAULT,
                                       DISABLED_DEFAULT, OutputReport)


class MockRegex:
    def __init__(self):
        self.pattern = '^fake-regex-pattern/$'


class MockRegexResolver:
    def __init__(self):
        self.pattern = '^fake-resolver/'


class MockRegexResolverNested:
    def __init__(self):
        self.pattern = '^fake-nested-resolver/'


class MockPattern:
    def __init__(self):
        self.regex = MockRegex()
        self.callback = 'fake-callback'
        self.name = 'fake-view-name'


class MockResolver:
    def __init__(self):
        self.url_patterns = [MockPattern()]
        self.regex = MockRegexResolver()
        self.app_name = 'fake-app-name'
        self.namespace = 'fake-namespace'


class MockResolverNested:
    def __init__(self):
        self.url_patterns = [MockResolver()]
        self.regex = MockRegexResolverNested()
        self.app_name = 'fake-app-name'
        self.namespace = 'nested-namespace'


class MockPatternDjango2:
    def __init__(self):
        self.pattern = '^fake-pattern/'
        self.callback = 'fake-callback'
        self.name = 'fake-view-name'


class MockPatternDjango2None:
    def __init__(self):
        self.pattern = '^fake-pattern/'
        self.callback = 'fake-callback'
        self.name = 'fake-view-none'


class MockResolverDjango2:
    def __init__(self):
        self.pattern = '^fake-resolver/'
        self.url_patterns = [MockPatternDjango2()]
        self.app_name = 'fake-app-name'
        self.namespace = 'fake-namespace'


class MockResolverDjango2None:
    def __init__(self):
        self.pattern = '^fake-resolver/'
        self.url_patterns = [MockPatternDjango2None()]
        self.app_name = None
        self.namespace = None


class MockResolverDjango2None2:
    def __init__(self):
        self.pattern = '^fake-resolver/'
        self.url_patterns = [MockResolverDjango2None()]
        self.app_name = 'fake-app-name'
        self.namespace = 'fake-namespace'


class MockResolverDjangoNested:
    def __init__(self):
        self.pattern = '^fake-nested-resolver/'
        self.url_patterns = [MockResolverDjango2()]
        self.app_name = 'fake-app-name'
        self.namespace = 'nested-namespace'


class UnitTestWalkSiteURL(UnitTestCase):

    def setUp(self):
        self.pattern_1 = MockPattern()
        self.data = [self.pattern_1]

    def test_second_param_is_optional_return_a_list(self):
        result = walk_site_url(self.data)
        self.assertIsInstance(result, list)

    def test_first_param_list_of_pattern_and_view(self):
        result = walk_site_url(self.data)
        self.assertEqual(result, [('fake-regex-pattern/', 'fake-callback',
                                   'fake-view-name', None)])

    def test_first_param_list_of_patterns_and_views(self):
        pattern_2 = MockPattern()
        pattern_2.regex.pattern = 'fake-regex-pattern-2/'
        pattern_2.callback = 'fake-view-2'
        result = walk_site_url([self.pattern_1, pattern_2])
        self.assertEqual(result, [('fake-regex-pattern/', 'fake-callback',
                                   'fake-view-name', None),
                                  ('fake-regex-pattern-2/', 'fake-view-2',
                                   'fake-view-name', None)])

    def test_param_list_with_pattern_and_resolver_django_1(self):
        expected_result = [
            ('fake-regex-pattern/', 'fake-callback', 'fake-view-name', None),
            ('fake-resolver/fake-regex-pattern/',
             'fake-callback', 'fake-namespace:fake-view-name', 'fake-app-name'
             )]
        resolver = MockResolver()
        result = walk_site_url([self.pattern_1, resolver])
        self.assertEqual(result, expected_result)

    def test_param_list_with_pattern_and_nested_resolver_django_1(self):
        expected_result = [
            ('fake-regex-pattern/', 'fake-callback', 'fake-view-name', None),
            ('fake-nested-resolver/fake-resolver/fake-regex-pattern/',
             'fake-callback', 'nested-namespace:fake-namespace:fake-view-name',
             'fake-app-name'
             )
        ]
        resolver = MockResolverNested()
        result = walk_site_url([self.pattern_1, resolver])
        self.assertEqual(result, expected_result)

    def test_param_list_with_pattern_and_resolver_django_2(self):
        expected_result = [
            ('fake-pattern/', 'fake-callback', 'fake-view-name', None),
            ('fake-resolver/fake-pattern/',
             'fake-callback', 'fake-namespace:fake-view-name', 'fake-app-name'
             )
        ]
        resolver = MockResolverDjango2()
        result = walk_site_url([MockPatternDjango2(), resolver])
        self.assertEqual(result, expected_result)

    def test_param_list_with_pattern_and_nested_resolver_django_2(self):
        expected_result = [
            ('fake-pattern/', 'fake-callback', 'fake-view-name', None),
            ('fake-nested-resolver/fake-resolver/fake-pattern/',
             'fake-callback', 'nested-namespace:fake-namespace:fake-view-name',
             'fake-app-name'
             )
        ]
        result = walk_site_url([MockPatternDjango2(),
                                MockResolverDjangoNested()])
        self.assertEqual(result, expected_result)

    def test_param_list_with_resolver_get_app_name_and_view_name_django_1(self):
        expected_result = [
            ('fake-resolver/fake-regex-pattern/',
             'fake-callback', 'fake-namespace:fake-view-name', 'fake-app-name'
             ),
            ('fake-nested-resolver/fake-resolver/fake-regex-pattern/',
             'fake-callback', 'nested-namespace:fake-namespace:fake-view-name',
             'fake-app-name'
             )
        ]
        result = walk_site_url([MockResolver(), MockResolverNested()])
        self.assertEqual(result, expected_result)

    def test_param_list_with_resolver_get_app_name_and_view_name_django_2(self):
        expected_result = [
            ('fake-resolver/fake-pattern/',
             'fake-callback', 'fake-namespace:fake-view-name', 'fake-app-name'
             ),
            ('fake-nested-resolver/fake-resolver/fake-pattern/',
             'fake-callback', 'nested-namespace:fake-namespace:fake-view-name',
             'fake-app-name'
             )
        ]
        resolver = MockResolverDjango2()
        nested_resolver = MockResolverDjangoNested()
        result = walk_site_url([resolver, nested_resolver])
        self.assertEqual(result, expected_result)

    def test_when_url_namespace_is_None(self):
        expected_result = [
            ('fake-resolver/fake-resolver/fake-pattern/',
             'fake-callback', 'fake-view-none', None
             )
        ]
        resolver = MockResolverDjango2None2()
        result = walk_site_url([resolver])
        self.assertEqual(result, expected_result)

    # def test_when_view_name_is_None(self):
    #     expected_result = [
    #         ('fake-resolver/fake-pattern/',
    #          'fake-callback', 'fake-view-name', None
    #          )
    #     ]
    #     resolver = MockResolverDjango2None2()
    #     result = walk_site_url([resolver])
    #     print(result)
    #     self.assertEqual(result, expected_result)


class IntegratedTestWalkSiteURL(TestCase):

    def setUp(self):
        self.url = import_module(settings.ROOT_URLCONF).urlpatterns

    def test_found_direct_access_view(self):
        expected_result = ('direct_access_view/',
                           views.protected_view_by_role,
                           'direct_access_view', None)
        result = walk_site_url(self.url)
        self.assertIn(expected_result, result)

    def test_found_included_view_without_namespace(self):
        expected_result = ('role-included[135]/view_by_role/',
                           views.protected_view_by_role,
                           'django_roles_access:view_protected_by_role',
                           'django_roles_access')
        result = walk_site_url(self.url)
        self.assertIn(expected_result, result)

    def test_found_included_view_with_namespace(self):
        expected_result = ('role-included2/view_by_role/',
                           views.protected_view_by_role,
                           'app-ns2:view_protected_by_role',
                           'django_roles_access')
        result = walk_site_url(self.url)
        self.assertIn(expected_result, result)

    def test_found_nested_access_view(self):
        expected_result = ('nest1/nest2/view_by_role/',
                           views.protected_view_by_role,
                           'nest1_namespace:nest2_namespace:view_'
                           'protected_by_role',
                           'roles-app-name')
        result = walk_site_url(self.url)
        self.assertIn(expected_result, result)


class UnitTestGetViewsByApp(UnitTestCase):
    """
    get_views_by_app receive the result of walk_site_url and is required to
    return a dictionary with keys been installed applications.
    """
    def setUp(self):
        self.data = [('a', 'b', 'c', 'fake-app-1')]

    @patch('django_roles_access.utils.settings')
    def test_returns_a_dictionary(
            self, mock_settings
    ):
        mock_settings.INSTALLED_APPS = ['fake-app-1', 'fake-app-2']
        result = get_views_by_app(self.data)
        self.assertIsInstance(result, dict)

    @patch('django_roles_access.utils.settings')
    def test_returns_a_dictionary_with_all_installed_apps(
            self, mock_settings
    ):
        mock_settings.INSTALLED_APPS = ['fake-app-1', 'fake-app-2']
        result = get_views_by_app(self.data)
        assert 'fake-app-1' in result
        assert 'fake-app-2' in result

    @patch('django_roles_access.utils.settings')
    def test_values_of_returned_dictionary_keys_are_lists(
            self, mock_settings
    ):
        mock_settings.INSTALLED_APPS = ['fake-app-1', 'fake-app-2']
        result = get_views_by_app(self.data)
        self.assertIsInstance(result['fake-app-1'], list)
        self.assertIsInstance(result['fake-app-2'], list)

    @patch('django_roles_access.utils.settings')
    def test_receive_list_of_tuples_with_4_element(
            self, mock_settings
    ):
        mock_settings.INSTALLED_APPS = ['fake-app-1']
        result = get_views_by_app(self.data)
        assert 'fake-app-1' in result

    @patch('django_roles_access.utils.settings')
    def test_raise_type_error_if_receive_list_of_tuples_with_3_element(
            self, mock_settings
    ):
        mock_settings.INSTALLED_APPS = ['fake-app-1']
        data = [('a', 'b', 'c')]
        with self.assertRaises(TypeError):
            get_views_by_app(data)

    @patch('django_roles_access.utils.settings')
    def test_raise_type_error_if_receive_list_of_tuples_with_5_element(
            self, mock_settings
    ):
        mock_settings.INSTALLED_APPS = ['fake-app-1']
        data = [('a', 'b', 'c', 'd', 'e')]
        with self.assertRaises(TypeError):
            get_views_by_app(data)

    @patch('django_roles_access.utils.settings')
    def test_received_data_is_ordered_and_returned_by_application(
            self, mock_settings
    ):
        mock_settings.INSTALLED_APPS = ['fake-app-1', 'fake-app-2', None]
        data = [('a', 'b', 'c', 'fake-app-1'), ('1', '2', '3', 'fake-app-2'),
                ('a1', 'b2', 'c3', None)]
        expected_result = [('a', 'b', 'c')]
        result = get_views_by_app(data)
        self.assertEqual(expected_result, result['fake-app-1'])

    @patch('django_roles_access.utils.settings')
    def test_can_work_with_no_declared_application_name(
            self, mock_settings
    ):
        mock_settings.INSTALLED_APPS = ['fake-app-1', 'fake-app-2', None]
        data = [('a', 'b', 'c', 'fake-app-1'), ('1', '2', '3', 'fake-app-2'),
                ('a1', 'b2', 'c3', None)]
        expected_result = [('a1', 'b2', 'c3')]
        result = get_views_by_app(data)
        self.assertEqual(expected_result, result[APP_NAME_FOR_NONE])

    @patch('django_roles_access.utils.settings')
    def test_if_application_is_not_in_installed_apps_will_not_be_in_dict(
            self, mock_settings
    ):
        mock_settings.INSTALLED_APPS = ['fake-app-1', 'fake-app-2', None]
        result = get_views_by_app(self.data)
        assert 'fake-app-3' not in result


class IntegratedTestGetViewsByApp(TestCase):

    def setUp(self):
        self.url = import_module(settings.ROOT_URLCONF).urlpatterns
    
    def test_not_declared_app_are_recognized_as_undefined_app(self):
        expected_result = ('direct_access_view/',
                           views.protected_view_by_role,
                           'direct_access_view')
        result = get_views_by_app(walk_site_url(self.url))
        self.assertIn(expected_result, result[APP_NAME_FOR_NONE])

    def test_views_without_namespace_are_added_with_app_name_in_view_name(self):
        expected_result = ('role-included[135]/view_by_role/',
                           views.protected_view_by_role,
                           'django_roles_access:view_protected_by_role')
        result = get_views_by_app(walk_site_url(self.url))
        self.assertIn(expected_result, result['django_roles_access'])

    def test_view_with_namespace_are_added_with_correct_app_name(self):
        expected_result = ('role-included2/view_by_role/',
                           views.protected_view_by_role,
                           'app-ns2:view_protected_by_role')
        result = get_views_by_app(walk_site_url(self.url))
        self.assertIn(expected_result, result['django_roles_access'])

    def test_nested_namespace_are_added_with_correct_app_name(self):
        expected_result = ('nest1/nest2/view_by_role/',
                           views.protected_view_by_role,
                           'nest1_namespace:nest2_namespace:view_'
                           'protected_by_role')
        result = get_views_by_app(walk_site_url(self.url))
        self.assertIn(expected_result, result['roles-app-name'])


class TestGetViewAnalyzeReport(UnitTestCase):

    def test_report_for_no_application_type(self):
        expected = u'\t' + NONE_TYPE_DEFAULT
        result = get_view_analyze_report(None)
        self.assertEqual(result, expected)

    def test_report_for_application_type_NOT_SECURED(self):
        expected = u'\t' + NOT_SECURED_DEFAULT
        result = get_view_analyze_report('NOT_SECURED')
        self.assertEqual(result, expected)
        self.assertEqual(result, expected)

    def test_report_for_application_type_DISABLED(self):
        expected = u'\t' + DISABLED_DEFAULT
        result = get_view_analyze_report('DISABLED')
        self.assertEqual(result, expected)

    def test_report_for_application_type_SECURED(self):
        expected = u'\t' + SECURED_DEFAULT
        result = get_view_analyze_report('SECURED')
        self.assertEqual(result, expected)

    def test_report_for_application_type_PUBLIC(self):
        expected = u'\t' + PUBLIC_DEFAULT
        result = get_view_analyze_report('PUBLIC')
        self.assertEqual(result, expected)


class TestCheckDjangoRolesIsUsed(UnitTestCase):

    def test_detect_view_is_decorated(self):
        @access_by_role
        def function():
            pass
        self.assertTrue(check_django_roles_is_used(function))

    def test_detect_view_is_not_decorated(self):
        def function():
            pass
        self.assertFalse(check_django_roles_is_used(function()))

    def test_detect_view_use_mixin(self):
        class Aview(RolesMixin, TemplateView):
            template_name = 'dummyTemplate.html'
        self.assertTrue(check_django_roles_is_used(Aview))

    def test_detect_view_not_use_mixin(self):
        class Aview(TemplateView):
            template_name = 'dummyTemplate.html'
        self.assertFalse(check_django_roles_is_used(Aview))


@patch('django_roles_access.utils.ViewAccess')
class UnitTestAnalyzeByRoleAccess(UnitTestCase):

    def test_detect_access_is_by_role(
            self, mock_view_access
    ):
        expected = u'ERROR: No roles configured to access de view.'
        mock_view_access.type = 'br'
        mock_view_access.roles.count.return_value = 0
        result = analyze_by_role(mock_view_access)
        self.assertEqual(result, expected)

    def test_detect_access_is_not_by_role(
            self, mock_view_access
    ):
        expected = u''
        mock_view_access.type = 'pu'
        result = analyze_by_role(mock_view_access)
        self.assertEqual(result, expected)

    def test_detect_access_is_not_by_role_with_roles(
            self, mock_view_access
    ):
        expected = u'Roles with access: role-1, role-2'
        mock_view_access.type = 'br'
        role_1 = Mock()
        role_1.name = u'role-1'
        role_2 = Mock()
        role_2.name = u'role-2'
        mock_view_access.roles.all.return_value = [role_1, role_2]
        result = analyze_by_role(mock_view_access)
        self.assertEqual(result, expected)

    def test_detect_access_is_not_by_role_without_roles(
            self, mock_view_access
    ):
        expected = u'ERROR: No roles configured to access de view.'
        mock_view_access.type = 'br'
        mock_view_access.roles.count.return_value = 0
        result = analyze_by_role(mock_view_access)
        self.assertEqual(result, expected)


class IntegratedTestAnalyzeByRoleAccess(TestCase):

    def test_detect_access_is_by_role(self):
        expected = u'ERROR: No roles configured to access de view.'
        view_access = ViewAccess.objects.create(view='any-name', type='br')
        result = analyze_by_role(view_access)
        self.assertEqual(result, expected)

    def test_detect_access_is_not_by_role(self):
        expected = u''
        view_access = ViewAccess.objects.create(view='any-name', type='pu')
        result = analyze_by_role(view_access)
        self.assertEqual(result, expected)

    def test_detect_access_is_by_role_with_roles(self):
        expected = u'Roles with access: role-1, role-2'
        view_access = ViewAccess.objects.create(view='any-name', type='br')
        role_1, created = Group.objects.get_or_create(name='role-1')
        role_2, created = Group.objects.get_or_create(name='role-2')
        view_access.roles.add(role_1)
        view_access.roles.add(role_2)
        view_access.save()
        result = analyze_by_role(view_access)
        self.assertEqual(result, expected)

    def test_detect_access_is_not_by_role_without_roles(self):
        expected = u'ERROR: No roles configured to access de view.'
        view_access = ViewAccess.objects.create(view='any-name', type='br')
        result = analyze_by_role(view_access)
        self.assertEqual(result, expected)


@patch('django_roles_access.utils.ViewAccess.objects')
class UnitTestViewAnalyzer(UnitTestCase):

    def test_view_analyzer_return_a_report(
            self, mock_objects
    ):
        view_access = Mock()
        view_access.type = 'pu'
        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = view_access
        result = view_access_analyzer('fake-app-type', 'fake-callback',
                                      'fake-view-name', 'fake-site-active')
        try:
            self.assertIsInstance(result, unicode)
        except:
            self.assertIsInstance(result, str)

    def test_view_analyzer_search_view_access_for_the_view(
            self, mock_objects
    ):
        view_access = Mock()
        view_access.type = 'pu'
        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = view_access
        view_access_analyzer('fake-app-type', 'fake-callback',
                             'fake-view-name', 'fake-site-active')
        assert mock_objects.first.called

    def test_view_analyzer_search_view_access_for_the_view_once(
            self, mock_objects
    ):
        view_access = Mock()
        view_access.type = 'pu'
        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = view_access
        view_access_analyzer('fake-app-type', 'fake-callback',
                             'fake-view-name', 'fake-site-active')
        self.assertEqual(mock_objects.filter.call_count, 1)

    def test_view_analyzer_search_view_access_with_view_name(
            self, mock_objects
    ):
        view_access = Mock()
        view_access.type = 'pu'
        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = view_access
        view_access_analyzer('fake-app-type', 'fake-callback',
                             'fake-view-name', 'fake-site-active')
        mock_objects.filter.assert_called_once_with(view='fake-view-name')

    def test_view_access_type_when_site_active_and_exists_view_access(
            self, mock_objects
    ):
        expected = u'View access is of type Public.'
        view_access = Mock()
        view_access.type = 'pu'
        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = view_access
        result = view_access_analyzer('fake-app-type', 'fake-callback',
                                      'fake-view-name', True)
        self.assertEqual(result, expected)

    @patch('django_roles_access.utils.analyze_by_role')
    def test_view_access_type_by_role_call_analyze_by_role(
            self, mock_analyze_by_role, mock_objects
    ):
        view_access = Mock()
        view_access.type = 'br'
        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = view_access
        view_access_analyzer('fake-app-type', 'fake-callback',
                             'fake-view-name', True)
        assert mock_analyze_by_role.called

    @patch('django_roles_access.utils.analyze_by_role')
    def test_view_access_type_by_role_call_analyze_by_role_once(
            self, mock_analyze_by_role, mock_objects
    ):
        view_access = Mock()
        view_access.type = 'br'
        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = view_access
        view_access_analyzer('fake-app-type', 'fake-callback',
                             'fake-view-name', True)
        self.assertEqual(mock_analyze_by_role.call_count, 1)

    @patch('django_roles_access.utils.analyze_by_role')
    def test_view_access_type_by_role_call_analyze_by_role_with_view_access(
            self, mock_analyze_by_role, mock_objects
    ):
        view_access = Mock()
        view_access.type = 'br'
        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = view_access
        view_access_analyzer('fake-app-type', 'fake-callback',
                             'fake-view-name', True)
        mock_analyze_by_role.assert_called_once_with(view_access)

    def test_no_view_access_object_for_the_view_and_site_active_no_app_type(
            self, mock_objects
    ):
        expected = u'\t' + NONE_TYPE_DEFAULT
        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = None
        result = view_access_analyzer(None, 'fake-callback',
                                      'fake-view-name', True)
        self.assertEqual(result, expected)

    def test_no_view_access_object_and_site_active_app_type_NOT_SECURED(
            self, mock_objects
    ):
        expected = u'\t' + NOT_SECURED_DEFAULT
        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = None
        result = view_access_analyzer('NOT_SECURED', 'fake-callback',
                                      'fake-view-name', True)
        self.assertEqual(result, expected)

    def test_no_view_access_object_and_site_active_app_type_DISABLED(
            self, mock_objects
    ):
        expected = u'\t' + DISABLED_DEFAULT
        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = None
        result = view_access_analyzer('DISABLED', 'fake-callback',
                                      'fake-view-name', True)
        self.assertEqual(result, expected)

    def test_no_view_access_object_and_site_active_app_type_SECURED(
            self, mock_objects
    ):
        expected = u'\t' + SECURED_DEFAULT
        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = None
        result = view_access_analyzer('SECURED', 'fake-callback',
                                      'fake-view-name', True)
        self.assertEqual(result, expected)

    def test_no_view_access_object_and_site_active_app_type_PUBLIC(
            self, mock_objects
    ):
        expected = u'\t' + PUBLIC_DEFAULT
        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = None
        result = view_access_analyzer('PUBLIC', 'fake-callback',
                                      'fake-view-name', True)
        self.assertEqual(result, expected)

    def test_middleware_not_used_view_access_object_exist_and_dr_tools_used(
            self, mock_objects
    ):
        expected = u'View access is of type Public.'

        @access_by_role
        def function():
            pass
        view_access = Mock()
        view_access.type = 'pu'
        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = view_access
        result = view_access_analyzer('fake-app-type', function,
                                      'fake-view-name', False)
        self.assertEqual(result, expected)

    def test_middleware_not_used_view_access_object_exist_and_dr_tools_not_used(
            self, mock_objects
    ):
        expected = u'ERROR: View access object exist for the view, but no '
        expected += u'Django role access tool is used: neither decorator, '
        expected += u'mixin, or middleware.'

        def function():
            pass

        view_access = Mock()
        view_access.type = 'pu'
        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = view_access
        result = view_access_analyzer('fake-app-type', function,
                                      'fake-view-name', False)
        self.assertEqual(result, expected)

    def test_middleware_not_used_dr_tools_are_used_no_view_access_object(
            self, mock_objects
    ):
        expected = u'\t' + PUBLIC_DEFAULT

        @access_by_role
        def function():
            pass
        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = None
        result = view_access_analyzer('PUBLIC', function,
                                      'fake-view-name', False)
        self.assertEqual(result, expected)

    def test_no_django_roles_tools_used_no_application_type(
            self, mock_objects
    ):
        expected = u'No Django roles access tool used. Access to view depends '
        expected += u'on its implementation.'

        def function():
            pass
        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = None
        result = view_access_analyzer(None, function,
                                      'fake-view-name', False)
        self.assertEqual(result, expected)

    def test_no_django_roles_tools_used_application_type(
            self, mock_objects
    ):
        expected = u'No Django roles access tool used. Access to view depends '
        expected += u'on its implementation.'

        def function():
            pass
        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = None
        result = view_access_analyzer('Authorized', function,
                                      'fake-view-name', False)
        self.assertEqual(result, expected)


class IntegratedTestViewAnalyzezr(TestCase):

    def test_with_middleware_SECURED_without_view_access_object(self):
        expected = u'\t' + SECURED_DEFAULT
        result = view_access_analyzer(
            'SECURED', views.MiddlewareView.as_view,
            'django_roles_access:middleware_view_class',
            True)
        self.assertEqual(expected, result)

    def test_with_middleware_NOT_SECURED_with_view_access_object(self):
        ViewAccess.objects.create(
            view='django_roles_access:middleware_view_class',
            type='br')
        result = view_access_analyzer(
            'NOT_SECURED', views.MiddlewareView.as_view,
            'django_roles_access:middleware_view_class',
            True)
        self.assertEqual(result, u'\t' + NOT_SECURED_DEFAULT)

    def test_with_middleware_DISABLED_with_view_access_object(self):
        ViewAccess.objects.create(
            view='django_roles_access:middleware_view_class',
            type='pu')
        result = view_access_analyzer(
            'DISABLED', views.MiddlewareView.as_view,
            'django_roles_access:middleware_view_class',
            True)
        self.assertEqual(result, u'\t' + DISABLED_DEFAULT)

    def test_with_middleware_with_view_access_object(self):
        expected = u'View access is of type By role.'
        expected += u'ERROR: No roles configured to access de view.'
        ViewAccess.objects.create(
            view='django_roles_access:middleware_view_class',
            type='br')
        result = view_access_analyzer(
            'SECURED', views.MiddlewareView.as_view,
            'django_roles_access:middleware_view_class',
            True)
        self.assertEqual(result, expected)

    def test_with_middleware_with_view_access_object_with_roles(self):
        expected = u'View access is of type By role.'
        expected += u'Roles with access: test1, test2'
        g1, created = Group.objects.get_or_create(name='test1')
        g2, created = Group.objects.get_or_create(name='test2')
        view_access = ViewAccess.objects.create(
            view='django_roles_access:middleware_view_class',
            type='br')
        view_access.roles.add(g1)
        view_access.roles.add(g2)
        view_access.save()
        result = view_access_analyzer(
            'SECURED', views.MiddlewareView.as_view,
            'django_roles_access:middleware_view_class',
            True)
        self.assertEqual(result, expected)

    def test_with_middleware_with_view_access_object_authorized(self):
        expected = u'View access is of type Authorized.'
        ViewAccess.objects.create(
            view='django_roles_access:middleware_view_class',
            type='au')
        result = view_access_analyzer(
            'SECURED', views.MiddlewareView.as_view,
            'django_roles_access:middleware_view_class',
            True)
        self.assertEqual(result, expected)

    def test_with_middleware_with_view_access_object_public(self):
        expected = u'View access is of type Public.'
        ViewAccess.objects.create(
            view='django_roles_access:middleware_view_class',
            type='pu')
        result = view_access_analyzer(
            'SECURED', views.MiddlewareView.as_view,
            'django_roles_access:middleware_view_class',
            True)
        self.assertEqual(result, expected)

    def test_without_middleware_with_view_access_object(self):
        expected = u'View access is of type By role.'
        expected += u'ERROR: No roles configured to access de view.'
        ViewAccess.objects.create(
            view='django_roles_access:view_protected_by_role',
            type='br')
        result = view_access_analyzer(
            'SECURED', views.protected_view_by_role,
            'django_roles_access:view_protected_by_role',
            False)
        self.assertEqual(result, expected)

    def test_without_middleware_with_view_access_object_with_roles(self):
        expected = u'View access is of type By role.'
        expected += u'Roles with access: test1, test2'
        g1, created = Group.objects.get_or_create(name='test1')
        g2, created = Group.objects.get_or_create(name='test2')
        view_access = ViewAccess.objects.create(
            view='django_roles_access:view_protected_by_role',
            type='br')
        view_access.roles.add(g1)
        view_access.roles.add(g2)
        view_access.save()
        result = view_access_analyzer(
            'SECURED', views.protected_view_by_role,
            'django_roles_access:view_protected_by_role',
            False)
        self.assertEqual(result, expected)

    def test_without_middleware_with_view_access_object_authorized(self):
        expected = u'View access is of type Authorized.'
        ViewAccess.objects.create(
            view='django_roles_access:view_protected_by_role',
            type='au')
        result = view_access_analyzer(
            'SECURED', views.protected_view_by_role,
            'django_roles_access:view_protected_by_role',
            False)
        self.assertEqual(result, expected)

    def test_without_middleware_with_view_access_object_public(self):
        expected = u'View access is of type Public.'
        ViewAccess.objects.create(
            view='django_roles_access:view_protected_by_role',
            type='pu')
        result = view_access_analyzer(
            'SECURED', views.protected_view_by_role,
            'django_roles_access:view_protected_by_role',
            False)
        self.assertEqual(result, expected)

    def test_without_middleware_without_view_access_object_and_view_protected(
            self
    ):
        expected = u'\t' + SECURED_DEFAULT
        result = view_access_analyzer(
            'SECURED', views.protected_view_by_role,
            'django_roles_access:view_protected_by_role',
            False)
        self.assertEqual(result, expected)

    def test_without_middleware_no_view_access_object_and_view_protected_without_app(
            self
    ):
        expected = u'\t' + NONE_TYPE_DEFAULT

        result = view_access_analyzer(
            None, views.protected_view_by_role,
            'django_roles_access:view_protected_by_role',
            False)
        self.assertEqual(result, expected)

    def test_without_middleware_with_view_access_object_and_view_not_protected(
            self
    ):
        expected = u'ERROR: View access object exist for the view, '
        expected += 'but no Django role access tool is used: neither '
        expected += 'decorator, mixin, or middleware.'
        ViewAccess.objects.create(
            view='django_roles_access:middleware_view_func',
            type='pu')
        result = view_access_analyzer(
            None, views.middleware_view,
            'django_roles_access:middleware_view_func',
            False)
        self.assertEqual(result, expected)


class UnitTestOutputReport(UnitTestCase):

    def setUp(self):
        self.patch_mock_stdout = patch.object(BaseCommand(), 'style')
        self.patch_mock_style = patch.object(BaseCommand(), 'stdout')
        self.mock_stdout = self.patch_mock_stdout.start()
        self.mock_style = self.patch_mock_style.start()
        self._output = OutputReport(self.mock_stdout, self.mock_style)

    def tearDown(self):
        self.patch_mock_stdout.stop()
        self.patch_mock_style.stop()

    def test_initial_with_parameter(self):
        assert self._output.stdout == self.mock_stdout
        assert self._output.style == self.mock_style

    def test_internal_attributes_are_initialize(self):
        assert hasattr(self._output, '_row') and self._output._row == u''
        assert hasattr(self._output, '_format') and self._output._format == \
               'console'

    def test_initial_without_parameter(self):
        with self.assertRaises(TypeError) as e:
            OutputReport()

    def test_default_output_format_is_correct_type(self):
        assert self._output._format == 'console'

    def test_set_format(self):
        self._output.set_format('csv')
        assert self._output._format == 'csv'

    def test_add_to_row(self):
        self._output.add_to_row('text')
        self._output.add_to_row('other')
        self.assertIn('text', self._output._row)
        self.assertIn('other', self._output._row)

    def test_write_method_write_to_stdout(self):
        self._output.write(u'some text')
        assert self.mock_stdout.write.called

    def test_write_method_use_stdout_write_once(self):
        self._output.write(u'some text')
        self.assertEqual(self.mock_stdout.write.call_count, 1)

    def test_write_method_use_SUCCESS_style_for_styling_output(self):
        self._output.write(u'some text')
        self.mock_stdout.write.assert_called_once_with(
            self.mock_style.SUCCESS())

    def test_write_method_use_SUCCESS_style_for_output(self):
        self._output.write(u'some text')
        assert self.mock_style.SUCCESS.called

    def test_write_method_use_style_with_received_argument(self):
        self._output.write(u'some text')
        self.mock_style.SUCCESS.assert_called_once_with(u'some text')

    def test_console_format_write_correct_header_to_stdout_with_SUCCESS_style(
            self
    ):
        expected = u'Start checking views access.\n'
        expected += u'Start gathering information.'
        self._output.write_header()
        self.mock_style.SUCCESS.assert_called_once_with(expected)
        self.assertEqual(self.mock_stdout.write.call_count, 1)

    @patch('django_roles_access.utils.timezone')
    def test_cvs_format_write_correct_header(
            self, mock_timezone
    ):
        mock_timezone.now.return_value = 'fake-date'
        self._output.set_format('csv')
        self._output.write_header()
        self.mock_style.SUCCESS.assert_called_once_with(u'Reported: fake-date')
        self.assertEqual(self.mock_stdout.write.call_count, 1)

    def test_console_format_write_correct_middleware_status_and_end_of_header(
            self
    ):
        expected = u'Django roles access middleware is active: False.\n'
        self._output.write_middleware_status(False)
        self.mock_style.SUCCESS.assert_called_once_with(expected)
        self.assertEqual(self.mock_stdout.write.call_count, 1)

    def test_console_format_write_correct_end_of_header(
            self
    ):
        expected = u'Finish gathering information.'
        self._output.write_end_of_head()
        self.mock_style.SUCCESS.assert_called_once_with(expected)
        self.assertEqual(self.mock_stdout.write.call_count, 1)

    def test_cvs_format_write_correct_correct_middleware_status(
            self
    ):
        expected = u'Django roles access middleware is active: False.\n'
        self._output.set_format('csv')
        self._output.write_middleware_status(False)
        self.mock_style.SUCCESS.assert_called_once_with(expected)
        self.assertEqual(self.mock_stdout.write.call_count, 1)

    def test_cvs_format_write_correct_csv_columns(
            self
    ):
        expected = u'App Name,Type,View Name,Url,Status,Status description'
        self._output.set_format('csv')
        self._output.write_end_of_head()
        self.mock_style.SUCCESS.assert_called_once_with(expected)
        self.assertEqual(self.mock_stdout.write.call_count, 1)

    def test_console_format_process_app_data_to_stdout_with_SUCCESS_style(self):
        app_name = u'fake-app-name'
        app_type = u'fake-app-type'
        view_list = ['fake-view']
        expected = u'\tAnalyzing: {}\n'.format(app_name)
        expected += u'\t\t{} is {} type.'.format(app_name, app_type)
        self._output.process_application_data(app_name, app_type, view_list)
        self.mock_style.SUCCESS.assert_called_once_with(expected)
        self.assertEqual(self.mock_stdout.write.call_count, 1)

    def test_console_format_process_app_data_without_type(self):
        app_name = u'fake-app-name'
        app_type = None
        view_list = ['fake-view']
        expected = u'\tAnalyzing: {}\n'.format(app_name)
        expected += u'\t\t{} has no type.'.format(app_name)
        self._output.process_application_data(app_name, app_type, view_list)
        self.mock_style.SUCCESS.assert_called_once_with(expected)
        self.assertEqual(self.mock_stdout.write.call_count, 1)

    def test_console_format_process_app_data_without_views(self):
        app_name = u'fake-app-name'
        app_type = u'fake-app-type'
        view_list = []
        expected = u'\tAnalyzing: {}\n'.format(app_name)
        expected += u'\t\t{} is {} type.'.format(app_name, app_type)
        expected += u'\t\t{} does not have configured views.'.format(app_name)
        self._output.process_application_data(app_name, app_type, view_list)
        self.mock_style.SUCCESS.assert_called_once_with(expected)
        self.assertEqual(self.mock_stdout.write.call_count, 1)

    def test_cvs_format_process_application_data_to_string(self):
        app_name = u'fake-app-name'
        app_type = u'fake-app-type'
        view_list = ['fake-view-list']
        expected = u'{},{},'.format(app_name, app_type, view_list)
        self._output.set_format('csv')
        self._output.process_application_data(app_name, app_type, view_list)
        self.assertEqual(expected, self._output._row)

    def test_cvs_format_process_application_data_without_type_to_string(self):
        app_name = u'fake-app-name'
        app_type = None
        view_list = ['fake-view-list']
        expected = u'fake-app-name,no type,'.format(app_name)
        self._output.set_format('csv')
        self._output.process_application_data(app_name, app_type, view_list)
        self.assertEqual(expected, self._output._row)

    def test_cvs_format_process_application_data_without_views(self):
        app_name = u'fake-app-name'
        app_type = u'fake-app-type'
        view_list = []
        expected = u'fake-app-name,fake-app-type,,,,,'.format(app_name)
        self._output.set_format('csv')
        self._output.process_application_data(app_name, app_type, view_list)
        self.assertEqual(expected, self._output._row)

    def test_console_format_process_view_data_to_stdout_with_SUCCESS_style(
            self
    ):
        view_name = u'fake-view-name'
        url = '/fake-url/'
        expected = u'\n\t\tAnalysis for view: {}'.format(view_name)
        expected += u'\n\t\tView url: {}'.format(url)
        self._output.process_view_data(view_name, url)
        self.mock_style.SUCCESS.assert_called_once_with(expected)
        self.assertEqual(self.mock_stdout.write.call_count, 1)

    def test_cvs_format_process_view_data(self):
        view_name = u'fake-view-name'
        url = '/fake-url/'
        expected = u'{},{}'.format(view_name, url)
        self._output.set_format('csv')
        self._output.process_view_data(view_name, url)
        self.assertIn(expected, self._output._row)

    # View_access_analyzer output.
    def test_console_format_write_vaa_to_stdout(self):
        self._output.write_view_access_analyzer(u'some text')
        assert self.mock_stdout.write.called

    def test_console_format_use_stdout_write_once_with_vaa(self):
        self._output.write_view_access_analyzer(u'some text')
        self.assertEqual(self.mock_stdout.write.call_count, 1)

    def test_console_format_use_SUCCESS_style_for_styling_output_of_vaa(self):
        self._output.write_view_access_analyzer(u'some text')
        self.mock_stdout.write.assert_called_once_with(
            self.mock_style.SUCCESS())

    def test_console_format_use_SUCCESS_style_for_output_of_vaa(self):
        self._output.write_view_access_analyzer(u'some text')
        assert self.mock_style.SUCCESS.called

    def test_console_format_use_style_with_vaa_result(self):
        self._output.write_view_access_analyzer(u'some text')
        self.mock_style.SUCCESS.assert_called_once_with(u'\t\tsome text')

    def test_console_format_use_ERROR_style_for_output_if_error_in_vaa(self):
        self._output.write_view_access_analyzer('ERROR: fake report')
        assert self.mock_style.ERROR.called

    def test_console_format_use_ERROR_style_with_the_error_in_vaa(self):
        self._output.write_view_access_analyzer('ERROR: fake report')
        self.mock_style.ERROR.assert_called_once_with('\t\t' +
                                                      'ERROR: fake report')

    def test_console_format_use_WARNING_style_for_output_if_warning_in_vaa(self):
        self._output.write_view_access_analyzer('WARNING: fake report')
        assert self.mock_style.WARNING.called

    def test_console_format_use_WARNING_style_with_the_warning_in_vaa(self):
        self._output.write_view_access_analyzer('WARNING: fake report')
        self.mock_style.WARNING.assert_called_once_with(
            '\t\t' + 'WARNING: fake report')

    def test_csv_format_write_view_access_analyzer_with_Normal_to_stdout(self):
        self._output.add_to_row('fake-app,fake-type,fake-view,fake-url,')
        self._output._format = 'csv'
        self._output.write_view_access_analyzer(u'fake-report')
        self.assertEqual(self.mock_stdout.write.call_count, 1)

    def test_csv_format_write_view_access_analyzer_with_Normal_to_style(self):
        self._output.add_to_row('fake-app,fake-type,fake-view,fake-url,')
        expected = u'fake-app,fake-type,fake-view,fake-url,Normal,fake-report\n'
        self._output._format = 'csv'
        self._output.write_view_access_analyzer(u'fake-report')
        self.mock_style.SUCCESS.assert_called_once_with(expected)

    def test_csv_format_write_view_access_analyzer_with_WARNING_to_stdout(self):
        self._output.add_to_row('fake-app,fake-type,fake-view,fake-url,')
        self._output._format = 'csv'
        self._output.write_view_access_analyzer('WARNING: fake-report')
        self.assertEqual(self.mock_stdout.write.call_count, 1)

    def test_csv_format_write_view_access_analyzer_with_WARNING_with_style(
            self
    ):
        self._output.add_to_row('fake-app,fake-type,fake-view,fake-url,')
        expected = u'fake-app,fake-type,fake-view,fake-url,Warning,' \
                   u'fake-report\n'
        self._output._format = 'csv'
        self._output.write_view_access_analyzer('WARNING: fake-report')
        self.mock_style.WARNING.assert_called_once_with(expected)

    def test_csv_format_write_view_access_analyzer_with_ERROR_to_stdout(self):
        self._output.add_to_row('fake-app,fake-type,fake-view,fake-url,')
        self._output._format = 'csv'
        self._output.write_view_access_analyzer('ERROR: fake-report')
        self.assertEqual(self.mock_stdout.write.call_count, 1)

    def test_csv_format_write_view_access_analyzer_with_ERROR_with_style(self):
        self._output.add_to_row('fake-app,fake-type,fake-view,fake-url,')
        expected = u'fake-app,fake-type,fake-view,fake-url,Error,fake-report\n'
        self._output._format = 'csv'
        self._output.write_view_access_analyzer('ERROR: fake-report')
        self.mock_style.ERROR.assert_called_once_with(expected)

    def test_csv_format_write_view_access_analyzer_reset_OutputFormater_row(
            self
    ):
        self._output.add_to_row('fake-app,fake-type,fake-view,fake-url,')
        self._output._format = 'csv'
        self._output.write_view_access_analyzer('fake-report')
        self.assertEqual(self._output._row, u'fake-app,fake-type,')

    def test_console_format_close_application_data_to_stdout_with_SUCCESS_style(
            self
    ):
        expected = u'\tFinish analyzing fake-app-name.'
        self._output.close_application_data('fake-app-name')
        self.mock_style.SUCCESS.assert_called_once_with(expected)
        self.assertEqual(self.mock_stdout.write.call_count, 1)

    def test_cvs_format_close_application_data_to_string(self):
        expected = u''
        self._output.set_format('csv')
        self._output.close_application_data('fake-app-name')
        self.assertEqual(self._output._row, expected)

    def test_console_format_write_footer_to_stdout_with_SUCCESS_style(self):
        expected = u'End checking view access.'
        self._output.write_footer()
        self.mock_style.SUCCESS.assert_called_once_with(expected)
        self.assertEqual(self.mock_stdout.write.call_count, 1)

    def test_cvs_format_write_footer_to_string(self):
        expected = u'\n'
        self._output.set_format('csv')
        self._output.write_footer()
        self.assertEqual(self._output._row, expected)
