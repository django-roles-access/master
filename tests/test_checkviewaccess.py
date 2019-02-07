"""
This test module will search for all site's urls and analyze their security
status.
"""
try:
    from unittest.mock import Mock, patch, MagicMock
except:
    from mock import Mock, patch
from unittest.case import TestCase as UnitTestCase

from django.core.management import call_command
from django.test import TestCase


class UnitTestCheckViewAccess(UnitTestCase):

    def setUp(self):
        self.root_urlconf = Mock()

    @patch('django_roles.management.commands.checkviewaccess.import_module')
    @patch('django_roles.management.commands.checkviewaccess.settings')
    def test_import_module_is_called(
            self, mock_settings, mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        call_command('checkviewaccess')
        mock_import_module.assert_called()

    @patch('django_roles.management.commands.checkviewaccess.import_module')
    @patch('django_roles.management.commands.checkviewaccess.settings')
    def test_import_module_is_called_once(
            self, mock_settings, mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        call_command('checkviewaccess')
        mock_import_module.assert_called_once()

    @patch('django_roles.management.commands.checkviewaccess.import_module')
    @patch('django_roles.management.commands.checkviewaccess.settings')
    def test_import_module_is_called_once_with(
            self, mock_settings, mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        call_command('checkviewaccess')
        mock_import_module.assert_called_once_with(self.root_urlconf)

    @patch('django_roles.management.commands.checkviewaccess.walk_site_url')
    @patch('django_roles.management.commands.checkviewaccess.import_module')
    @patch('django_roles.management.commands.checkviewaccess.settings')
    def test_walk_site_url_is_called(
            self, mock_settings, mock_import_module, mock_walk_site_url
    ):
        mock_import_module.urlpatterns = 'fake-url-pattern'
        call_command('checkviewaccess')
        mock_walk_site_url.assert_called()

    @patch('django_roles.management.commands.checkviewaccess.walk_site_url')
    @patch('django_roles.management.commands.checkviewaccess.import_module')
    @patch('django_roles.management.commands.checkviewaccess.settings')
    def test_walk_site_url_is_called_once(
            self, mock_settings, mock_import_module, mock_walk_site_url
    ):
        mock_import_module.urlpatterns = 'fake-url-pattern'
        call_command('checkviewaccess')
        mock_walk_site_url.assert_called_once()

    @patch('django_roles.management.commands.checkviewaccess.walk_site_url')
    @patch('django_roles.management.commands.checkviewaccess.import_module')
    @patch('django_roles.management.commands.checkviewaccess.settings')
    def test_walk_site_url_is_called_once_with(
            self, mock_settings, mock_import_module, mock_walk_site_url
    ):
        urlpatterns = Mock()
        urlpatterns.urlpatterns = 'fake-urlpatterns'
        mock_import_module.return_value = urlpatterns
        call_command('checkviewaccess')
        mock_walk_site_url.assert_called_once_with('fake-urlpatterns')


class AnalyzeSiteSecurity(TestCase):
    """
    The main class for analyzing site security.

    In this context *site security* means:
    * All site's urls have been recover and analyzed.
    * The uls analyze is: for the called view:
      a Recover view's security from :class:`roles.models.SecurityAccess`.
      b If there is no object related with the view:
        + Check for application configuration:
          a If application si **public**. Is OK.
          b If application is **no public**: TEST if login is required for the
            view. In **no public** application the default behavior is to
            require login if there is no :class:`roles.models.SecurityAccess`
            object related with the view (to minimize administrative tasks).
      c If there is an SecurityAccess object for the view:
        + TEST: The access to the view must be protected as object instruct.

    The tests to be done are:
    1 TEST if login is required for a view without related
      :class:`roles.models.SecurityAccess` object and belonging to a NOT
      PUBLIC application.
    2 TEST if the access configured for the view is correct against the
    information found in :class:`roles.models.SecurityAccess` object.

    Expected result
    ~~~~~~~~~~~~~~~

    * Fail: When between all possible site's url, there is one or more views
      that:
      a Or Fail TEST 1
      b Or Fail TEST 2
      c The view has escape all possibilities.


    Things to be tested
    If a view use *login_required*, site test should warn this, and if
    possible, test if it is OK. In other words, it will be OK if site test
    detect that user need to be logged in.
    """
    pass

# from unittest.case import TestCase
# import pytest
#
# from roles.utils import get_applications_view_names
# from roles.models import SecurityAccess

# class TestSiteSecurity(TestCase):
#     """
#     This test will check the security across the site (or Django project).
#
#     Some thing to take think about:
#     """
#
#     @pytest.mark.django_db
#     def test_site_security(self):
#         no_configured_views = []
#         from src.urls import urlpatterns
#         # print(urlpatterns)
#         for app_name, view_name in get_applications_view_names():
#             url_name = '{}:{}'.format(app_name, view_name)
#             configuration = SecurityAccess.objects.filter(url_name__iexact=url_name)
#             if configuration.count() == 0:
#                 no_configured_views.append(url_name)
#         if len(no_configured_views) > 0:
#             self.fail(u'The next Django\'s URLs: {} do not have a security configured'.format(
#                 no_configured_views))
#         self.assertTrue(True)
