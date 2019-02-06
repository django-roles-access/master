from unittest.mock import Mock, patch
from unittest import TestCase as UnitTestCase

from django_roles.utils import walk_site_url


class UnitTestWalkSiteURL(UnitTestCase):
    def setUp(self):
        self.pattern_1 = Mock()
        self.pattern_1.regex.pattern = 'fake-regex-pattern/'
        self.pattern_1.callback = 'fake-view'
        self.data = [self.pattern_1]

    def test_second_param_is_optional_return_a_list(self):
        result = walk_site_url(self.data)
        self.assertIsInstance(result, list)

    def test_first_param_list_of_pattern_and_view(self):
        result = walk_site_url(self.data)
        self.assertEqual(result, [('fake-regex-pattern/', 'fake-view')])

    def test_first_param_list_of_patterns_and_views(self):
        pattern_2 = Mock()
        pattern_2.regex.pattern = 'fake-regex-pattern-2/'
        pattern_2.callback = 'fake-view-2'
        result = walk_site_url([self.pattern_1, pattern_2])
        self.assertEqual(result, [('fake-regex-pattern/', 'fake-view'),
                                  ('fake-regex-pattern-2/', 'fake-view-2')])

