from django.utils.six import StringIO
from django.utils.translation import ugettext as _
try:
    from unittest.mock import Mock, patch, MagicMock
except:
    from mock import Mock, patch
from unittest.case import TestCase as UnitTestCase

from django.core.management import call_command, BaseCommand
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

    @patch('django_roles.management.commands.checkviewaccess.'
           'view_access_analyzer')
    def test_view_analyzer_is_called_0_times_when_app_have_no_views(
            self, mock_view_access_analyzer, mock_settings, mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        call_command('checkviewaccess')
        self.assertEqual(mock_view_access_analyzer.call_count, 0)

    @patch('django_roles.management.commands.checkviewaccess.get_views_by_app')
    @patch('django_roles.management.commands.checkviewaccess.'
           'view_access_analyzer')
    def test_view_analyzer_is_called_3_times_when_app_have_3_views(
            self, mock_view_access_analyzer, mock_view_by_app, mock_settings,
            mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        mock_view_by_app.return_value = {'fake-app':
                                         [('/fake1/', 'fake-callback-1',
                                           'fake-view-1'),
                                          ('/fake2/', 'fake-callback-2',
                                           'fake-view-1'),
                                          ('/fake3/', 'fake-callback-3',
                                           'fake-view-1')]}
        mock_view_access_analyzer.return_value = u'fake-analysis'
        call_command('checkviewaccess')
        self.assertEqual(mock_view_access_analyzer.call_count, 3)

    @patch('django_roles.management.commands.checkviewaccess.get_views_by_app')
    @patch('django_roles.management.commands.checkviewaccess.'
           'view_access_analyzer')
    @patch('django_roles.management.commands.checkviewaccess.get_app_type')
    def test_view_analyzer_is_called_1_times_with_params(
            self, mock_get_app_type, mock_view_access_analyzer,
            mock_view_by_app, mock_settings, mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        mock_view_by_app.return_value = {'fake-app':
                                         [('/fake1/', 'fake-callback-1',
                                           'fake-view-1')]}
        mock_get_app_type.return_value = 'fake-app-type'
        mock_view_access_analyzer.return_value = u'fake-analysis'
        call_command('checkviewaccess')
        mock_view_access_analyzer.assert_called_with('fake-app-type',
                                                     'fake-callback-1',
                                                     'fake-view-1', False)

    @patch('django_roles.management.commands.checkviewaccess.get_views_by_app')
    @patch('django_roles.management.commands.checkviewaccess.'
           'view_access_analyzer')
    def test_view_name_is_reported(
            self, mock_view_access_analyzer, mock_view_by_app, mock_settings,
            mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        mock_view_by_app.return_value = {'fake-app':
                                         [('/fake1/', 'fake-callback-1',
                                           'fake-view')]}
        out = StringIO()
        expected_text = _(u'Analysis for view: fake-view')
        mock_view_access_analyzer.return_value = u'fake-analysis'
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_text, out.getvalue())

    @patch('django_roles.management.commands.checkviewaccess.get_views_by_app')
    @patch('django_roles.management.commands.checkviewaccess.'
           'view_access_analyzer')
    def test_view_url_is_reported(
            self, mock_view_access_analyzer, mock_view_by_app, mock_settings,
            mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        mock_view_by_app.return_value = {'fake-app':
                                         [('/fake1/', 'fake-callback-1',
                                           'fake-view')]}
        mock_view_access_analyzer.return_value = u'fake-analysis'
        out = StringIO()
        expected_text = _(u'View url: /fake1/')
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_text, out.getvalue())

    @patch('django_roles.management.commands.checkviewaccess.get_views_by_app')
    @patch('django_roles.management.commands.checkviewaccess.'
           'view_access_analyzer')
    @patch('django_roles.management.commands.checkviewaccess'
           '.print_view_analysis')
    def test_print_view_analyzer_is_called_1_times(
            self, mock_print_view_analysis, mock_view_access_analyzer,
            mock_view_by_app, mock_settings, mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        mock_view_by_app.return_value = {'fake-app':
                                         [('/fake1/', 'fake-callback-1',
                                           'fake-view')]}
        mock_view_access_analyzer.return_value = u'fake-analysis'
        call_command('checkviewaccess')
        mock_print_view_analysis.assert_called_once()

    # @patch('django_roles.management.commands.checkviewaccess.get_views_by_app')
    # @patch('django_roles.management.commands.checkviewaccess.'
    #        'view_access_analyzer')
    # def test_report_view_access_analysis(
    #         self, mock_view_access_analyzer,
    #         mock_view_by_app, mock_settings, mock_import_module
    # ):
    #     mock_settings.ROOT_URLCONF = self.root_urlconf
    #     mock_view_by_app.return_value = {'fake-app':
    #                                      [('/fake1/', 'fake-callback-1',
    #                                        'fake-view')]}
    #     mock_view_access_analyzer.return_value = u'All OK.'
    #     out = StringIO()
    #     call_command('checkviewaccess', stdout=out)
    #     self.assertIn(u'All OK', out.getvalue())


    # Test if checkview access show ERROR with Error color and warnings with
    # warning colors.
