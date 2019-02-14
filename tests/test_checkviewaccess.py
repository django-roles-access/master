"""
This test module will search for all site's urls and analyze their security
status.

Seguir la documentacion: para cada aplicacion indicar cual es su clasificacion

"""
from django.utils.six import StringIO
from django.utils.translation import ugettext as _
try:
    from unittest.mock import Mock, patch, MagicMock
except:
    from mock import Mock, patch
from unittest.case import TestCase as UnitTestCase

from django.core.management import call_command
from django.test import TestCase


@patch('django_roles.management.commands.checkviewaccess.import_module')
@patch('django_roles.management.commands.checkviewaccess.settings')
class UnitTestCheckViewAccess(UnitTestCase):

    def setUp(self):
        self.root_urlconf = Mock()

    def test_write_at_beginning_of_command_execution(
            self, mock_settings, mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        out = StringIO()
        expected_text = _(u'Start checking views access.')
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_text, out.getvalue())

    def test_write_when_finish_command_execution(
            self, mock_settings, mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        out = StringIO()
        expected_text = _(u'End checking view access.')
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_text, out.getvalue())

    def test_write_at_beginning_of_gathering_information_phase(
            self, mock_settings, mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        out = StringIO()
        expected_text = _(u'Start gathering information.')
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_text, out.getvalue())

    def test_import_module_is_called(
            self, mock_settings, mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        call_command('checkviewaccess')
        mock_import_module.assert_called()

    def test_import_module_is_called_once(
            self, mock_settings, mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        call_command('checkviewaccess')
        mock_import_module.assert_called_once()

    def test_import_module_is_called_once_with(
            self, mock_settings, mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        call_command('checkviewaccess')
        mock_import_module.assert_called_once_with(self.root_urlconf)

    @patch('django_roles.management.commands.checkviewaccess.walk_site_url')
    def test_walk_site_url_is_called(
            self, mock_walk_site_url, mock_settings, mock_import_module
    ):
        mock_import_module.urlpatterns = 'fake-url-pattern'
        call_command('checkviewaccess')
        mock_walk_site_url.assert_called()

    @patch('django_roles.management.commands.checkviewaccess.walk_site_url')
    def test_walk_site_url_is_called_once(
            self, mock_walk_site_url, mock_settings, mock_import_module
    ):
        mock_import_module.urlpatterns = 'fake-url-pattern'
        call_command('checkviewaccess')
        mock_walk_site_url.assert_called_once()

    @patch('django_roles.management.commands.checkviewaccess.walk_site_url')
    def test_walk_site_url_is_called_once_with(
            self, mock_walk_site_url, mock_settings, mock_import_module
    ):
        urlpatterns = Mock()
        urlpatterns.urlpatterns = 'fake-urlpatterns'
        mock_import_module.return_value = urlpatterns
        call_command('checkviewaccess')
        mock_walk_site_url.assert_called_once_with('fake-urlpatterns')

    @patch('django_roles.management.commands.checkviewaccess.get_views_by_app')
    def test_get_views_by_app_is_called(
            self, mock_get_views_by_app, mock_settings, mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        call_command('checkviewaccess')
        mock_get_views_by_app.assert_called()

    @patch('django_roles.management.commands.checkviewaccess.get_views_by_app')
    def test_get_views_by_app_is_called_once(
            self, mock_get_views_by_app, mock_settings, mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        call_command('checkviewaccess')
        mock_get_views_by_app.assert_called_once()

    @patch('django_roles.management.commands.checkviewaccess.walk_site_url')
    @patch('django_roles.management.commands.checkviewaccess.get_views_by_app')
    def test_get_views_by_app_is_called_once_with(
            self, mock_get_views_by_app, mock_walk_site_url, mock_settings,
            mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        mock_walk_site_url.return_value = 'fake-result'
        call_command('checkviewaccess')
        mock_get_views_by_app.assert_called_once_with('fake-result')

    @patch('django_roles.management.commands.checkviewaccess.'
           'get_setting_dictionary')
    def test_get_setting_dictionary_is_called(
            self, mock_get_setting_dictionary, mock_settings, mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        call_command('checkviewaccess')
        mock_get_setting_dictionary.assert_called()

    @patch('django_roles.management.commands.checkviewaccess.'
           'get_setting_dictionary')
    def test_get_setting_dictionary_is_called_once(
            self, mock_get_setting_dictionary, mock_settings, mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        call_command('checkviewaccess')
        mock_get_setting_dictionary.assert_called_once()

    def test_write_at_end_of_gathering_information_phase(
            self, mock_settings, mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        out = StringIO()
        expected_text = _(u'Finish gathering information.')
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_text, out.getvalue())

    def test_middleware_is_active_and_site_active_is_true(
            self, mock_settings, mock_import_module
    ):
        mock_settings.MIDDLEWARE = ['fake-middleware',
                                    'django_roles.middleware.RolesMiddleware',
                                    'other-fake-middleware']
        mock_settings.ROOT_URLCONF = self.root_urlconf
        out = StringIO()
        expected_text = _(u'Django roles active for site: True.')
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_text, out.getvalue())

    def test_middleware_is_not_active_and_site_active_is_false(
            self, mock_settings, mock_import_module
    ):
        mock_settings.MIDDLEWARE = ['fake-middleware',
                                    'other-fake-middleware']
        mock_settings.ROOT_URLCONF = self.root_urlconf
        out = StringIO()
        expected_text = _(u'Django roles active for site: False.')
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_text, out.getvalue())

    @patch('django_roles.utils.settings')
    def test_write_at_start_of_each_application_analyze(
            self, mock_utils_settings, mock_settings, mock_import_module
    ):
        mock_utils_settings.INSTALLED_APPS = ['fake-app-1', 'fake-app-2']
        mock_settings.ROOT_URLCONF = self.root_urlconf
        out = StringIO()
        expected_text1 = _(u'Analyzing fake-app-1:')
        expected_text2 = _(u'Analyzing fake-app-2:')
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_text1, out.getvalue())
        self.assertIn(expected_text2, out.getvalue())

    @patch('django_roles.utils.settings')
    def test_write_at_end_of_each_application_analyze(
            self, mock_utils_settings, mock_settings, mock_import_module
    ):
        mock_utils_settings.INSTALLED_APPS = ['fake-app-1', 'fake-app-2']
        mock_settings.ROOT_URLCONF = self.root_urlconf
        out = StringIO()
        expected_text1 = _(u'Finish analyzing fake-app-1.')
        expected_text2 = _(u'Finish analyzing fake-app-2.')
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_text1, out.getvalue())
        self.assertIn(expected_text2, out.getvalue())

    @patch('django_roles.utils.settings')
    def test_detect_installed_application_is_not_configured(
            self, mock_utils_settings, mock_settings, mock_import_module
    ):
        mock_utils_settings.INSTALLED_APPS = ['fake-app-1']
        mock_settings.ROOT_URLCONF = self.root_urlconf
        out = StringIO()
        expected_text = _(u'fake-app-1 has no type.')
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_text, out.getvalue())

    @patch('django_roles.management.commands.checkviewaccess.get_app_type')
    @patch('django_roles.utils.settings')
    def test_get_app_type_is_called(
            self, mock_utils_settings, mock_get_app_type, mock_settings,
            mock_import_module
    ):
        mock_utils_settings.INSTALLED_APPS = ['fake-app-1']
        mock_settings.ROOT_URLCONF = self.root_urlconf
        call_command('checkviewaccess')
        mock_get_app_type.assert_called()

    @patch('django_roles.management.commands.checkviewaccess.get_app_type')
    @patch('django_roles.utils.settings')
    def test_get_app_type_is_called_for_each_installed_app_0(
            self, mock_utils_settings, mock_get_app_type, mock_settings,
            mock_import_module
    ):
        mock_utils_settings.INSTALLED_APPS = []
        mock_settings.ROOT_URLCONF = self.root_urlconf
        call_command('checkviewaccess')
        self.assertEqual(mock_get_app_type.call_count, 0)

    @patch('django_roles.management.commands.checkviewaccess.get_app_type')
    @patch('django_roles.utils.settings')
    def test_get_app_type_is_called_for_each_installed_app_3(
            self, mock_utils_settings, mock_get_app_type, mock_settings,
            mock_import_module
    ):
        mock_utils_settings.INSTALLED_APPS = ['fake-app-1', 'fake-app-2', 'bla']
        mock_settings.ROOT_URLCONF = self.root_urlconf
        call_command('checkviewaccess')
        self.assertEqual(mock_get_app_type.call_count, 3)

    @patch('django_roles.utils.settings')
    @patch('django_roles.tools.settings')
    def test_detect_installed_application_is_configured_as_NOT_SECURED(
            self, mock_tools_settings, mock_utils_settings, mock_settings,
            mock_import_module
    ):
        mock_utils_settings.INSTALLED_APPS = ['fake-app']
        mock_tools_settings.NOT_SECURED = ['fake-app']
        mock_settings.ROOT_URLCONF = self.root_urlconf
        out = StringIO()
        expected_text = _(u'fake-app is NOT_SECURED type.')
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_text, out.getvalue())

    @patch('django_roles.utils.settings')
    @patch('django_roles.tools.settings')
    def test_detect_installed_application_is_configured_as_PUBLIC(
            self, mock_tools_settings, mock_utils_settings, mock_settings,
            mock_import_module
    ):
        mock_utils_settings.INSTALLED_APPS = ['fake-app']
        mock_tools_settings.PUBLIC = ['fake-app']
        mock_settings.ROOT_URLCONF = self.root_urlconf
        out = StringIO()
        expected_text = _(u'fake-app is PUBLIC type.')
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_text, out.getvalue())

    @patch('django_roles.utils.settings')
    @patch('django_roles.tools.settings')
    def test_detect_installed_application_is_configured_as_SECURED(
            self, mock_tools_settings, mock_utils_settings, mock_settings,
            mock_import_module
    ):
        mock_utils_settings.INSTALLED_APPS = ['fake-app']
        mock_tools_settings.SECURED = ['fake-app']
        mock_settings.ROOT_URLCONF = self.root_urlconf
        out = StringIO()
        expected_text = _(u'fake-app is SECURED type.')
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_text, out.getvalue())


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
