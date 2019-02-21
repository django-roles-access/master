from functools import wraps
from importlib import import_module
from unittest import TestCase as UnitTestCase

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.test import TestCase
from django.views.generic import TemplateView

from django_roles.decorator import access_by_role
from django_roles.mixin import RolesMixin
from tests import views

try:
    from unittest.mock import Mock, patch, MagicMock
except:
    from mock import Mock, patch

from django_roles.utils import (walk_site_url, get_views_by_app,
                                view_access_analyzer, get_view_analyze_report,
                                check_django_roles_is_used, APP_NAME_FOR_NONE)


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


class MockResolverDjango2:
    def __init__(self):
        self.pattern = '^fake-resolver/'
        self.url_patterns = [MockPatternDjango2()]
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
                           'django_roles:view_protected_by_role',
                           'django_roles')
        result = walk_site_url(self.url)
        self.assertIn(expected_result, result)

    def test_found_included_view_with_namespace(self):
        expected_result = ('role-included2/view_by_role/',
                           views.protected_view_by_role,
                           'app-ns2:view_protected_by_role',
                           'django_roles')
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

    @patch('django_roles.utils.settings')
    def test_returns_a_dictionary(
            self, mock_settings
    ):
        mock_settings.INSTALLED_APPS = ['fake-app-1', 'fake-app-2']
        result = get_views_by_app(self.data)
        self.assertIsInstance(result, dict)

    @patch('django_roles.utils.settings')
    def test_returns_a_dictionary_with_all_installed_apps(
            self, mock_settings
    ):
        mock_settings.INSTALLED_APPS = ['fake-app-1', 'fake-app-2']
        result = get_views_by_app(self.data)
        assert 'fake-app-1' in result
        assert 'fake-app-2' in result

    @patch('django_roles.utils.settings')
    def test_values_of_returned_dictionary_keys_are_lists(
            self, mock_settings
    ):
        mock_settings.INSTALLED_APPS = ['fake-app-1', 'fake-app-2']
        result = get_views_by_app(self.data)
        self.assertIsInstance(result['fake-app-1'], list)
        self.assertIsInstance(result['fake-app-2'], list)

    @patch('django_roles.utils.settings')
    def test_receive_list_of_tuples_with_4_element(
            self, mock_settings
    ):
        mock_settings.INSTALLED_APPS = ['fake-app-1']
        result = get_views_by_app(self.data)
        assert 'fake-app-1' in result

    @patch('django_roles.utils.settings')
    def test_raise_type_error_if_receive_list_of_tuples_with_3_element(
            self, mock_settings
    ):
        mock_settings.INSTALLED_APPS = ['fake-app-1']
        data = [('a', 'b', 'c')]
        with self.assertRaises(TypeError):
            get_views_by_app(data)

    @patch('django_roles.utils.settings')
    def test_raise_type_error_if_receive_list_of_tuples_with_5_element(
            self, mock_settings
    ):
        mock_settings.INSTALLED_APPS = ['fake-app-1']
        data = [('a', 'b', 'c', 'd', 'e')]
        with self.assertRaises(TypeError):
            get_views_by_app(data)

    @patch('django_roles.utils.settings')
    def test_received_data_is_ordered_and_returned_by_application(
            self, mock_settings
    ):
        mock_settings.INSTALLED_APPS = ['fake-app-1', 'fake-app-2', None]
        data = [('a', 'b', 'c', 'fake-app-1'), ('1', '2', '3', 'fake-app-2'),
                ('a1', 'b2', 'c3', None)]
        expected_result = [('a', 'b', 'c')]
        result = get_views_by_app(data)
        self.assertEqual(expected_result, result['fake-app-1'])

    @patch('django_roles.utils.settings')
    def test_can_work_with_no_declared_application_name(
            self, mock_settings
    ):
        mock_settings.INSTALLED_APPS = ['fake-app-1', 'fake-app-2', None]
        data = [('a', 'b', 'c', 'fake-app-1'), ('1', '2', '3', 'fake-app-2'),
                ('a1', 'b2', 'c3', None)]
        expected_result = [('a1', 'b2', 'c3')]
        result = get_views_by_app(data)
        self.assertEqual(expected_result, result[APP_NAME_FOR_NONE])

    @patch('django_roles.utils.settings')
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
                           'django_roles:view_protected_by_role')
        result = get_views_by_app(walk_site_url(self.url))
        self.assertIn(expected_result, result['django_roles'])

    def test_view_with_namespace_are_added_with_correct_app_name(self):
        expected_result = ('role-included2/view_by_role/',
                           views.protected_view_by_role,
                           'app-ns2:view_protected_by_role')
        result = get_views_by_app(walk_site_url(self.url))
        self.assertIn(expected_result, result['django_roles'])

    def test_nested_namespace_are_added_with_correct_app_name(self):
        expected_result = ('nest1/nest2/view_by_role/',
                           views.protected_view_by_role,
                           'nest1_namespace:nest2_namespace:view_'
                           'protected_by_role')
        result = get_views_by_app(walk_site_url(self.url))
        self.assertIn(expected_result, result['roles-app-name'])


class UnitTestViewAnalyzeReport(UnitTestCase):

    def test_report_for_no_application_type(self):
        expected = u'\tERROR: Django roles middleware is active; or view is '
        expected += u'protected with Django roles decorator or mixin, '
        expected += u'and has no application or application has no type. '
        expected += u'Is not possible to determine default behavior for view '
        expected += u'access.'
        result = get_view_analyze_report(None)
        self.assertEqual(result, expected)

    def test_report_for_application_type_NOT_SECURED(self):
        expected = u'\tWARNING: View has no security configured (ViewAccess) '
        expected += u'and application type is "NOT_SECURED". No access is '
        expected += u'checked at all.'
        result = get_view_analyze_report('NOT_SECURED')
        self.assertEqual(result, expected)

    def test_report_for_application_type_SECURED(self):
        expected = u'\tNo security configured for the view (ViewAccess object) '
        expected += u'and application type is "SECURED". User is required to '
        expected += u'be authenticated to access the view.'
        result = get_view_analyze_report('SECURED')
        self.assertEqual(result, expected)

    def test_report_for_application_type_PUBLIC(self):
        expected = u'\tNo security configured for the view (ViewAccess object) '
        expected += u'and application type is "PUBLIC". Anonymous user can '
        expected += u'access the view.'
        result = get_view_analyze_report('PUBLIC')
        self.assertEqual(result, expected)


class UnitTestCheckDjangoRolesIsUsed(UnitTestCase):

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


@patch('django_roles.utils.ViewAccess.objects')
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
        mock_objects.first.assert_called()

    def test_view_analyzer_search_view_access_for_the_view_once(
            self, mock_objects
    ):
        view_access = Mock()
        view_access.type = 'pu'
        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = view_access
        view_access_analyzer('fake-app-type', 'fake-callback',
                             'fake-view-name', 'fake-site-active')
        mock_objects.filter.assert_called_once()

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
        expected = u'\tView access is of type Public.'
        view_access = Mock()
        view_access.type = 'pu'
        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = view_access
        result = view_access_analyzer('fake-app-type', 'fake-callback',
                                      'fake-view-name', True)
        self.assertEqual(result, expected)

    def test_view_access_type_by_role_when_site_active(
            self, mock_objects
    ):
        expected = u'\tView access is of type By role.\n'
        expected += u'\tRoles with access: fake-role, fake-role-2'
        view_access = Mock()
        view_access.type = 'br'
        view_access.roles.all.return_value = ['fake-role', 'fake-role-2']
        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = view_access
        result = view_access_analyzer('fake-app-type', 'fake-callback',
                                      'fake-view-name', True)
        self.assertEqual(result, expected)

    def test_report_error_if_access_type_is_br_and_no_roles_added(
            self, mock_objects
    ):
        expected = u'\tView access is of type By role.\n'
        expected += u'\tERROR: No roles configured to access de view.'
        view_access = Mock()
        view_access.type = 'br'
        view_access.roles.count.return_value = 0
        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = view_access
        result = view_access_analyzer('fake-app-type', 'fake-callback',
                                      'fake-view-name', True)
        self.assertEqual(result, expected)

    def test_no_view_access_object_for_the_view_and_site_active_no_app_type(
            self, mock_objects
    ):
        expected = u'\tERROR: Django roles middleware is active; or view is '
        expected += u'protected with Django roles decorator or mixin, '
        expected += u'and has no application or application has no type. '
        expected += u'Is not possible to determine default behavior for view '
        expected += u'access.'
        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = None
        result = view_access_analyzer(None, 'fake-callback',
                                      'fake-view-name', True)
        self.assertEqual(result, expected)

    def test_no_view_access_object_and_site_active_app_type_NOT_SECURED(
            self, mock_objects
    ):
        expected = u'\tWARNING: View has no security configured (ViewAccess) '
        expected += u'and application type is "NOT_SECURED". No access is '
        expected += u'checked at all.'
        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = None
        result = view_access_analyzer('NOT_SECURED', 'fake-callback',
                                      'fake-view-name', True)
        self.assertEqual(result, expected)

    def test_no_view_access_object_and_site_active_app_type_SECURED(
            self, mock_objects
    ):
        expected = u'\tNo security configured for the view (ViewAccess object) '
        expected += u'and application type is "SECURED". User is required to '
        expected += u'be authenticated to access the view.'
        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = None
        result = view_access_analyzer('SECURED', 'fake-callback',
                                      'fake-view-name', True)
        self.assertEqual(result, expected)

    def test_no_view_access_object_and_site_active_app_type_PUBLIC(
            self, mock_objects
    ):
        expected = u'\tNo security configured for the view (ViewAccess object) '
        expected += u'and application type is "PUBLIC". Anonymous user can '
        expected += u'access the view.'
        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = None
        result = view_access_analyzer('PUBLIC', 'fake-callback',
                                      'fake-view-name', True)
        self.assertEqual(result, expected)

    def test_middleware_not_used_view_access_object_exist_and_dr_tools_used(
            self, mock_objects
    ):
        expected = u'\tView access is of type Public.'
        view_access = Mock()
        view_access.type = 'pu'
        mock_objects.filter.return_value = mock_objects
        mock_objects.first.return_value = view_access
        result = view_access_analyzer('fake-app-type', 'fake-callback',
                                      'fake-view-name', False)
        self.assertEqual(result, expected)


# class UnitTestGetViewDecorators(UnitTestCase):
#
#     def test_return_list(self):
#
#         def test_function():
#             pass
#
#         result = get_view_decorators(test_function)
#         self.assertIsInstance(result, list)
#
#     def test_return_view_function(self):
#
#         def test_function():
#             pass
#
#         expected = ['test_function']
#         result = get_view_decorators(test_function)
#         self.assertEqual(result, expected)
#
#     def test_return_view_function_decorator(self):
#
#         def myattr_dec(func):
#             def wrapper(*args, **kwargs):
#                 return func(*args, **kwargs)
#             return wrapper
#
#         @myattr_dec
#         def test_function():
#             pass
#
#         @login_required
#         def login_function():
#             pass
#
#         expected = ['myattr_dec', 'test_function']
#         # import pdb
#         # pdb.set_trace()
#         # result = get_view_decorators(test_function)
#
#         result2 = get_view_decorators(login_function)
#         self.assertEqual(result2, expected)

