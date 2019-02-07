from unittest import TestCase as UnitTestCase
try:
    from unittest.mock import Mock, patch, MagicMock
except:
    from mock import Mock, patch

from django_roles.utils import walk_site_url


class MockRegex:
    def __init__(self):
        self.pattern = '^fake-regex-pattern/'


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


