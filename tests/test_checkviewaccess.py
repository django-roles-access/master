from django.conf import settings
from django.contrib.auth.models import Group
try:
    from django.utils.six import StringIO
except:
    from io import StringIO

from django_roles_access.models import ViewAccess

try:
    from unittest.mock import Mock, patch, MagicMock, ANY, PropertyMock
except:
    from mock import Mock, patch, ANY, PropertyMock
from unittest.case import TestCase as UnitTestCase

from django.core.management import call_command
from django.test import TestCase, modify_settings
from django_roles_access.utils import (NONE_TYPE_DEFAULT, NOT_SECURED_DEFAULT,
                                       APP_NAME_FOR_NONE)


@patch('django_roles_access.management.commands.checkviewaccess'
       '.OutputFormater')
@patch('django_roles_access.management.commands.checkviewaccess.import_module')
@patch('django_roles_access.management.commands.checkviewaccess.settings')
class UnitTestCheckViewAccessCommon(UnitTestCase):

    def setUp(self):
        self.root_urlconf = Mock()

    def test_OutputFormater_is_called(
            self, mock_settings, mock_import_module, mock_otuput_formater
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        call_command('checkviewaccess')
        assert mock_otuput_formater.called

    def test_OutputFormater_is_called_once(
            self, mock_settings, mock_import_module, mock_otuput_formater
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        call_command('checkviewaccess')
        self.assertEqual(mock_otuput_formater.call_count, 1)

    @patch('django_roles_access.management.commands.checkviewaccess.Command'
           '.style', create=True, new_callable=PropertyMock)
    @patch('django_roles_access.management.commands.checkviewaccess.Command'
           '.stdout', create=True, new_callable=PropertyMock)
    def test_OutputFormater_is_called_once_with(
            self, mock_stdout, mock_style, mock_settings,
            mock_import_module, mock_output_formater
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        stdout = mock_stdout.return_value
        style = mock_style.return_value
        call_command('checkviewaccess')
        mock_output_formater.assert_called_once_with(stdout, style)

    def test_import_module_is_called(
            self, mock_settings, mock_import_module, mock_otuput_formater
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        call_command('checkviewaccess')
        assert mock_import_module.called

    def test_import_module_is_called_once(
            self, mock_settings, mock_import_module, mock_otuput_formater
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        call_command('checkviewaccess')
        self.assertEqual(mock_import_module.call_count, 1)

    def test_import_module_is_called_once_with(
            self, mock_settings, mock_import_module, mock_otuput_formater
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        call_command('checkviewaccess')
        mock_import_module.assert_called_once_with(self.root_urlconf)

    @patch('django_roles_access.management.commands.checkviewaccess.walk_site_url')
    def test_walk_site_url_is_called(
            self, mock_walk_site_url, mock_settings, mock_import_module,
            mock_otuput_formater
    ):
        mock_import_module.urlpatterns = 'fake-url-pattern'
        call_command('checkviewaccess')
        assert mock_walk_site_url.called

    @patch('django_roles_access.management.commands.checkviewaccess.walk_site_url')
    def test_walk_site_url_is_called_once(
            self, mock_walk_site_url, mock_settings, mock_import_module,
            mock_otuput_formater
    ):
        mock_import_module.urlpatterns = 'fake-url-pattern'
        call_command('checkviewaccess')
        self.assertEqual(mock_walk_site_url.call_count, 1)

    @patch('django_roles_access.management.commands.checkviewaccess.walk_site_url')
    def test_walk_site_url_is_called_once_with(
            self, mock_walk_site_url, mock_settings, mock_import_module,
            mock_otuput_formater
    ):
        urlpatterns = Mock()
        urlpatterns.urlpatterns = 'fake-urlpatterns'
        mock_import_module.return_value = urlpatterns
        call_command('checkviewaccess')
        mock_walk_site_url.assert_called_once_with('fake-urlpatterns')

    @patch('django_roles_access.management.commands.checkviewaccess.get_views_by_app')
    def test_get_views_by_app_is_called(
            self, mock_get_views_by_app, mock_settings, mock_import_module,
            mock_otuput_formater
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        call_command('checkviewaccess')
        assert mock_get_views_by_app.called

    @patch('django_roles_access.management.commands.checkviewaccess.get_views_by_app')
    def test_get_views_by_app_is_called_once(
            self, mock_get_views_by_app, mock_settings, mock_import_module,
            mock_otuput_formater
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        call_command('checkviewaccess')
        self.assertEqual(mock_get_views_by_app.call_count, 1)

    @patch('django_roles_access.management.commands.checkviewaccess.walk_site_url')
    @patch('django_roles_access.management.commands.checkviewaccess.get_views_by_app')
    def test_get_views_by_app_is_called_once_with(
            self, mock_get_views_by_app, mock_walk_site_url, mock_settings,
            mock_import_module, mock_otuput_formater
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        mock_walk_site_url.return_value = 'fake-result'
        call_command('checkviewaccess')
        mock_get_views_by_app.assert_called_once_with('fake-result')


@patch('django_roles_access.management.commands.checkviewaccess.import_module')
@patch('django_roles_access.management.commands.checkviewaccess.settings')
class UnitTestCheckViewAccessWithoutArguments(UnitTestCase):

    def setUp(self):
        self.root_urlconf = Mock()

    @patch('django_roles_access.management.commands.checkviewaccess'
           '.OutputFormater.set_format')
    def test_format_attribute_is_not_set(
            self, mock_set_format, mock_settings, mock_import_module
    ):

        call_command('checkviewaccess')
        assert not mock_set_format.called

    def test_write_at_beginning_of_command_execution(
            self, mock_settings, mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        out = StringIO()
        expected_text = u'Start checking views access.'
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_text, out.getvalue())

    def test_write_when_finish_command_execution(
            self, mock_settings, mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        out = StringIO()
        expected_text = u'End checking view access.'
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_text, out.getvalue())

    def test_write_at_beginning_of_gathering_information_phase(
            self, mock_settings, mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        out = StringIO()
        expected_text = u'Start gathering information.'
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_text, out.getvalue())

    def test_write_at_end_of_gathering_information_phase(
            self, mock_settings, mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        out = StringIO()
        expected_text = u'Finish gathering information.'
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_text, out.getvalue())

    def test_middleware_is_active_and_site_active_is_true(
            self, mock_settings, mock_import_module
    ):
        mock_settings.MIDDLEWARE = ['fake-middleware',
                                    'django_roles_access.middleware.RolesMiddleware',
                                    'other-fake-middleware']
        mock_settings.ROOT_URLCONF = self.root_urlconf
        out = StringIO()
        expected_text = u'Django roles access middleware is active: True.'
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_text, out.getvalue())

    def test_middleware_is_not_active_and_site_active_is_false(
            self, mock_settings, mock_import_module
    ):
        mock_settings.MIDDLEWARE = ['fake-middleware',
                                    'other-fake-middleware']
        mock_settings.ROOT_URLCONF = self.root_urlconf
        out = StringIO()
        expected_text = u'Django roles access middleware is active: False.'
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_text, out.getvalue())

    @patch('django_roles_access.utils.settings')
    def test_write_at_start_of_each_application_analyze(
            self, mock_utils_settings, mock_settings, mock_import_module
    ):
        mock_utils_settings.INSTALLED_APPS = ['fake-app-1', 'fake-app-2']
        mock_settings.ROOT_URLCONF = self.root_urlconf
        out = StringIO()
        expected_text1 = u'Analyzing fake-app-1:'
        expected_text2 = u'Analyzing fake-app-2:'
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_text1, out.getvalue())
        self.assertIn(expected_text2, out.getvalue())

    @patch('django_roles_access.utils.settings')
    def test_write_at_end_of_each_application_analyze(
            self, mock_utils_settings, mock_settings, mock_import_module
    ):
        mock_utils_settings.INSTALLED_APPS = ['fake-app-1', 'fake-app-2']
        mock_settings.ROOT_URLCONF = self.root_urlconf
        out = StringIO()
        expected_text1 = u'Finish analyzing fake-app-1.'
        expected_text2 = u'Finish analyzing fake-app-2.'
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_text1, out.getvalue())
        self.assertIn(expected_text2, out.getvalue())

    @patch('django_roles_access.utils.settings')
    def test_detect_installed_application_is_not_configured(
            self, mock_utils_settings, mock_settings, mock_import_module
    ):
        mock_utils_settings.INSTALLED_APPS = ['fake-app-1']
        mock_settings.ROOT_URLCONF = self.root_urlconf
        out = StringIO()
        expected_text = u'fake-app-1 has no type.'
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_text, out.getvalue())

    @patch('django_roles_access.management.commands.checkviewaccess.get_app_type')
    @patch('django_roles_access.utils.settings')
    def test_get_app_type_is_called(
            self, mock_utils_settings, mock_get_app_type, mock_settings,
            mock_import_module
    ):
        mock_utils_settings.INSTALLED_APPS = ['fake-app-1']
        mock_settings.ROOT_URLCONF = self.root_urlconf
        call_command('checkviewaccess')
        assert mock_get_app_type.called

    @patch('django_roles_access.management.commands.checkviewaccess.get_app_type')
    @patch('django_roles_access.utils.settings')
    def test_get_app_type_is_called_for_each_installed_app_0(
            self, mock_utils_settings, mock_get_app_type, mock_settings,
            mock_import_module
    ):
        mock_utils_settings.INSTALLED_APPS = []
        mock_settings.ROOT_URLCONF = self.root_urlconf
        call_command('checkviewaccess')
        self.assertEqual(mock_get_app_type.call_count, 0)

    @patch('django_roles_access.management.commands.checkviewaccess.get_app_type')
    @patch('django_roles_access.utils.settings')
    def test_get_app_type_is_called_for_each_installed_app_3(
            self, mock_utils_settings, mock_get_app_type, mock_settings,
            mock_import_module
    ):
        mock_utils_settings.INSTALLED_APPS = ['fake-app-1', 'fake-app-2', 'bla']
        mock_settings.ROOT_URLCONF = self.root_urlconf
        call_command('checkviewaccess')
        self.assertEqual(mock_get_app_type.call_count, 3)

    @patch('django_roles_access.utils.settings')
    @patch('django_roles_access.tools.settings')
    def test_detect_installed_application_is_configured_as_NOT_SECURED(
            self, mock_tools_settings, mock_utils_settings, mock_settings,
            mock_import_module
    ):
        mock_utils_settings.INSTALLED_APPS = ['fake-app']
        mock_tools_settings.NOT_SECURED = ['fake-app']
        mock_settings.ROOT_URLCONF = self.root_urlconf
        out = StringIO()
        expected_text = u'fake-app is NOT_SECURED type.'
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_text, out.getvalue())

    @patch('django_roles_access.utils.settings')
    @patch('django_roles_access.tools.settings')
    def test_detect_installed_application_is_configured_as_PUBLIC(
            self, mock_tools_settings, mock_utils_settings, mock_settings,
            mock_import_module
    ):
        mock_utils_settings.INSTALLED_APPS = ['fake-app']
        mock_tools_settings.PUBLIC = ['fake-app']
        mock_settings.ROOT_URLCONF = self.root_urlconf
        out = StringIO()
        expected_text = u'fake-app is PUBLIC type.'
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_text, out.getvalue())

    @patch('django_roles_access.utils.settings')
    @patch('django_roles_access.tools.settings')
    def test_detect_installed_application_is_configured_as_SECURED(
            self, mock_tools_settings, mock_utils_settings, mock_settings,
            mock_import_module
    ):
        mock_utils_settings.INSTALLED_APPS = ['fake-app']
        mock_tools_settings.SECURED = ['fake-app']
        mock_settings.ROOT_URLCONF = self.root_urlconf
        out = StringIO()
        expected_text = u'fake-app is SECURED type.'
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_text, out.getvalue())

    @patch('django_roles_access.management.commands.checkviewaccess.'
           'view_access_analyzer')
    def test_view_analyzer_is_called_0_times_when_app_have_no_views(
            self, mock_view_access_analyzer, mock_settings, mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        call_command('checkviewaccess')
        self.assertEqual(mock_view_access_analyzer.call_count, 0)

    @patch('django_roles_access.management.commands.checkviewaccess.get_views_by_app')
    def test_when_app_have_no_views_it_is_reported(
            self, mock_get_views_by_app, mock_settings, mock_import_module
    ):
        mock_get_views_by_app.return_value = {
            'fake-app-name': []
        }
        mock_settings.ROOT_URLCONF = self.root_urlconf
        out = StringIO()
        expected_text = u'\t\t{} does not have configured views.'.format(
            'fake-app-name')
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_text, out.getvalue())

    @patch('django_roles_access.management.commands.checkviewaccess.get_views_by_app')
    @patch('django_roles_access.management.commands.checkviewaccess.'
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

    @patch('django_roles_access.management.commands.checkviewaccess.get_views_by_app')
    @patch('django_roles_access.management.commands.checkviewaccess.'
           'view_access_analyzer')
    @patch('django_roles_access.management.commands.checkviewaccess.get_app_type')
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

    @patch('django_roles_access.management.commands.checkviewaccess.get_views_by_app')
    @patch('django_roles_access.management.commands.checkviewaccess.'
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
        expected_text = u'Analysis for view: fake-view'
        mock_view_access_analyzer.return_value = u'fake-analysis'
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_text, out.getvalue())

    @patch('django_roles_access.management.commands.checkviewaccess.get_views_by_app')
    @patch('django_roles_access.management.commands.checkviewaccess.'
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
        expected_text = u'View url: /fake1/'
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_text, out.getvalue())

    @patch('django_roles_access.management.commands.checkviewaccess.get_views_by_app')
    @patch('django_roles_access.management.commands.checkviewaccess.'
           'view_access_analyzer')
    @patch('django_roles_access.management.commands.checkviewaccess'
           '.OutputFormater.write_view_access_analyzer')
    def test_write_report_view_analyzer_is_called_1_times(
            self, mock_write_report, mock_view_access_analyzer,
            mock_view_by_app, mock_settings, mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        mock_view_by_app.return_value = {'fake-app':
                                         [('/fake1/', 'fake-callback-1',
                                           'fake-view')]}
        mock_view_access_analyzer.return_value = u'fake-analysis'
        call_command('checkviewaccess')
        self.assertEqual(mock_write_report.call_count, 1)

    @patch('django_roles_access.management.commands.checkviewaccess.get_views_by_app')
    @patch('django_roles_access.management.commands.checkviewaccess.'
           'view_access_analyzer')
    @patch('django_roles_access.management.commands.checkviewaccess'
           '.OutputFormater.write_view_access_analyzer')
    def test_write_report_view_analyzer_is_called_1_times_with_param(
            self, mock_write_report,
            mock_view_access_analyzer, mock_view_by_app, mock_settings,
            mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        mock_view_by_app.return_value = {'fake-app':
                                         [('/fake1/', 'fake-callback-1',
                                           'fake-view')]}
        mock_view_access_analyzer.return_value = u'fake-analysis'
        call_command('checkviewaccess')
        mock_write_report.assert_called_once_with(u'fake-analysis')


@patch('django_roles_access.management.commands.checkviewaccess.import_module')
@patch('django_roles_access.management.commands.checkviewaccess.settings')
class UnitTestCheckViewAccessCSVOutput(UnitTestCase):

    def setUp(self):
        self.root_urlconf = Mock()

    def test_action_accept_output_argument(
            self, mock_settings, mock_import_module
    ):
        call_command('checkviewaccess', '--output-format', 'csv')

    @patch('django_roles_access.management.commands.checkviewaccess'
           '.OutputFormater.set_format')
    def test_format_attribute_is_set_to_csv(
            self, mock_set_format, mock_settings, mock_import_module
    ):

        call_command('checkviewaccess', '--output-format', 'csv')
        mock_set_format.assert_called_once_with('csv')

    @patch('django_roles_access.management.commands.checkviewaccess.timezone')
    def test_first_line_output_is_report_date(
            self, mock_timezone, mock_settings, mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        out = StringIO()
        mock_timezone.now.return_value = 'fake-date'
        expected = u'Reported: fake-date'
        call_command('checkviewaccess', '--output-format', 'csv',
                     stdout=out)
        result = out.getvalue()
        expected_result = result.split('\n')[0]
        self.assertIn(expected, expected_result)

    def test_report_if_django_roles_access_middleware_is_active(
            self, mock_settings, mock_import_module
    ):
        mock_settings.MIDDLEWARE = ['fake-middleware',
                                    'django_roles_access.middleware.RolesMiddleware',
                                    'other-fake-middleware']
        mock_settings.ROOT_URLCONF = self.root_urlconf
        out = StringIO()
        expected = u'Django roles access middleware is active: True'
        call_command('checkviewaccess', '--output-format', 'csv',
                     stdout=out)
        result = out.getvalue()
        expected_result = result.split('\n')[1]
        self.assertIn(expected, expected_result)

    def test_report_if_django_roles_access_middleware_is_not_active(
            self, mock_settings, mock_import_module
    ):
        mock_settings.MIDDLEWARE = ['fake-middleware',
                                    'other-fake-middleware']
        mock_settings.ROOT_URLCONF = self.root_urlconf
        out = StringIO()
        expected = u'Django roles access middleware is active: False'
        call_command('checkviewaccess', '--output-format', 'csv',
                     stdout=out)
        result = out.getvalue()
        expected_result = result.split('\n')[1]
        self.assertIn(expected, expected_result)

    def test_write_csv_columns_name(
            self, mock_settings, mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        out = StringIO()
        expected = u'App Name,Type,View Name,Url,Status,Status description'
        call_command('checkviewaccess', '--output-format', 'csv',
                     stdout=out)
        result = out.getvalue()
        expected_result = result.split('\n')[2]
        self.assertIn(expected, expected_result)

    @patch('django_roles_access.management.commands.checkviewaccess'
           '.get_views_by_app')
    @patch('django_roles_access.management.commands.checkviewaccess.'
           'view_access_analyzer')
    @patch('django_roles_access.management.commands.checkviewaccess'
           '.get_app_type')
    def test_write_rows(
            self, mock_get_app_type, mock_view_access_analyzer,
            mock_get_views_by_app, mock_settings,mock_import_module
    ):
        """
        Normal case: There is app name, it has a type, there is also a view
        name.
        """
        def view_analyze(app_type, callback, view_name, site_active):
            if view_name is None:
                return None
            if view_name == 'fake-view-1':
                return '1-analyze'
            if view_name == 'fake-view-2':
                return 'ERROR: 2-analyze'
            if view_name == 'fake-view-3':
                return 'WARNING: 3-analyze'

        mock_settings.ROOT_URLCONF = self.root_urlconf
        mock_get_views_by_app.return_value = {'fake-app':
                                              [('/fake1/', 'fake-callback-1',
                                                'fake-view-1'),
                                               ('/fake2/', 'fake-callback-2',
                                                'fake-view-2'),
                                               ('/fake3/', 'fake-callback-3',
                                                'fake-view-3')]
                                              }
        mock_view_access_analyzer.side_effect = view_analyze
        mock_get_app_type.return_value = 'fake-type'
        out = StringIO()
        call_command('checkviewaccess', '--output-format', 'csv',
                     stdout=out)
        result = out.getvalue()
        expected1 = 'fake-app,fake-type,fake-view-1,/fake1/,Normal,1-analyze'
        expected2 = 'fake-app,fake-type,fake-view-2,/fake2/,Error,2-analyze'
        expected3 = 'fake-app,fake-type,fake-view-3,/fake3/,Warning,3-analyze'
        expected_result = result.split('\n')
        self.assertEqual(expected_result[3], expected1)
        self.assertEqual(expected_result[4], expected2)
        self.assertEqual(expected_result[5], expected3)

    def test_no_write_csv_ending_data(
            self, mock_settings, mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        out = StringIO()
        expected1 = u'django.contrib.admin,app has no type,,,,'
        expected2 = u'django.contrib.auth,app has no type,,,,'
        expected3 = u'django.contrib.contenttypes,app has no type,,,,'
        expected4 = u'django.contrib.sessions,app has no type,,,,'
        expected5 = u'django_roles_access,app has no type,,,,'
        expected6 = u''
        call_command('checkviewaccess', '--output-format', 'csv',
                     stdout=out)
        result = out.getvalue()
        self.assertIn(expected1, result)
        self.assertIn(expected2, result)
        self.assertIn(expected3, result)
        self.assertIn(expected4, result)
        self.assertIn(expected5, result)
        self.assertEqual(expected6, result.split('\n')[8])


class IntegratedTestCheckViewAccess(TestCase):
    """
    Cases:
    * Test default cases: no View objects for the view but Django role tool is
      used and application has type: NOT_SECURED, PUBLIC, AUTHORIZED, By role.

    * Test no application type: no View objects for the view but Django role
      tool is used and application has no type.

    * Test no configuration: no View objects for the view, no Django role
      tool is used. and application has type and application has no type.
    """

    # RED = '\x1b[31;1m'
    # GREEN = '\x1b[32;1m'
    # WARNING = '\x1b[33;1m'
    # ATTRIBUTES_OFF = '\x1b[0m'
    NO_APP_TYPE_ERROR = u'ERROR: Django roles middleware is active; or view ' \
                        u'is protected with Django roles decorator or mixin, ' \
                        u'and has no application or application has no type. ' \
                        u'There are no View Access object for the view. Is ' \
                        u'not possible to determine behavior for access view.'

    NOT_SECURED_DEFAULT = u'WARNING: View has no security configured ' \
                          u'(ViewAccess) and application type is ' \
                          u'"NOT_SECURED". No access is checked at all.'

    def setUp(self):
        # Clean up
        try:
            settings.__delattr__('NOT_SECURED')
        except:
            pass
        try:
            settings.__delattr__('PUBLIC')
        except:
            pass
        try:
            settings.__delattr__('SECURED')
        except:
            pass

    def test_no_django_roles_tools_used(self):
        expected_1 = u'\n\tAnalyzing django_roles:'
        expected_1 += u'\n\t\tdjango_roles has no type.'
        # expected = self.GREEN + '\n\t\t'
        expected_2 = u'Analysis for view: app-ns2:middleware_view_func\n'
        expected_2 += u'\t\tView url: role-included2/middleware_view_func/'
        # expected += self.ATTRIBUTES_OFF + '\n' + self.GREEN
        expected_2 += u'\n\t\tNo Django roles tool used. Access to '
        expected_2 += u'view depends on its implementation.'
        out = StringIO()
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())

    def test_no_django_roles_used_no_view_access_object_no_application(
            self
    ):
        expected_1 = u'\n\tAnalyzing {}:'.format(APP_NAME_FOR_NONE)
        expected_2 = u'Analysis for view: direct_view\n'
        expected_2 += u'\t\tView url: direct_view/'
        expected_2 += u'\n\t\tNo Django roles tool used. Access to '
        expected_2 += u'view depends on its implementation.'
        out = StringIO()
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())

    def test_no_django_roles_used_no_view_access_object_no_application_type(
            self
    ):
        expected_1 = u'\n\tAnalyzing {}:'.format(APP_NAME_FOR_NONE)
        expected_1 += u'\n\t\t{} has no type.'.format(APP_NAME_FOR_NONE)
        expected_2 = u'Analysis for view: direct_view\n'
        expected_2 += u'\t\tView url: direct_view/'
        expected_2 += u'\n\t\tNo Django roles tool used. Access to '
        expected_2 += u'view depends on its implementation.'
        out = StringIO()
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())

    def test_no_django_roles_used_no_view_access_object_app_type_SECURED(self):
        settings.__setattr__('SECURED', ['django_roles'])
        expected_1 = u'\n\tAnalyzing django_roles:'
        expected_1 += u'\n\t\tdjango_roles is SECURED type.'
        expected_2 = u'Analysis for view: app-ns2:middleware_view_func\n'
        expected_2 += u'\t\tView url: role-included2/middleware_view_func/'
        expected_2 += u'\n\t\tNo Django roles tool used. Access to '
        expected_2 += u'view depends on its implementation.'
        out = StringIO()
        call_command('checkviewaccess', stdout=out)
        settings.__delattr__('SECURED')
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())

    def test_decorator_no_view_access_object_app_type_None(self):
        expected_1 = u'\n\tAnalyzing django_roles:'
        expected_1 += u'\n\t\tdjango_roles has no type.'
        expected_2 = u'Analysis for view: app-ns2:view_protected_by_role\n'
        expected_2 += u'\t\tView url: role-included2/view_by_role/'
        expected_2 += u'\n\t\t' + NONE_TYPE_DEFAULT
        out = StringIO()
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())

    def test_decorator_no_view_access_object_app_type_NOT_SECURED(self):
        settings.__setattr__('NOT_SECURED', ['django_roles'])
        expected_1 = u'\n\tAnalyzing django_roles:'
        expected_1 += u'\n\t\tdjango_roles is NOT_SECURED type.'
        expected_2 = u'Analysis for view: app-ns2:view_protected_by_role\n'
        expected_2 += u'\t\tView url: role-included2/view_by_role/'
        expected_2 += u'\n\t\t' + NOT_SECURED_DEFAULT
        out = StringIO()
        call_command('checkviewaccess', stdout=out)
        settings.__delattr__('NOT_SECURED')
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())

    def test_decorator_no_view_access_object_app_type_SECURED(self):
        settings.__setattr__('SECURED', ['django_roles'])
        expected_1 = u'\n\tAnalyzing django_roles:'
        expected_1 += u'\n\t\tdjango_roles is SECURED type.'
        expected_2 = u'Analysis for view: app-ns2:view_protected_by_role\n'
        expected_2 += u'\t\tView url: role-included2/view_by_role/'
        expected_2 += u'\n\t\t'
        out = StringIO()
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())
        settings.__delattr__('SECURED')

    def test_decorator_no_view_access_object_app_type_PUBLIC(self):
        settings.__setattr__('PUBLIC', ['django_roles'])
        expected_1 = u'\n\tAnalyzing django_roles:'
        expected_1 += u'\n\t\tdjango_roles is PUBLIC type.'
        expected_2 = u'Analysis for view: app-ns2:view_protected_by_role\n'
        expected_2 += u'\t\tView url: role-included2/view_by_role/'
        expected_2 += u'\n\t\t'
        out = StringIO()
        call_command('checkviewaccess', stdout=out)
        settings.__delattr__('PUBLIC')
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())

    def test_decorator_view_access_object_app_type_None(self):
        expected_1 = u'\n\tAnalyzing django_roles:'
        expected_1 += u'\n\t\tdjango_roles has no type.'
        expected_2 = u'Analysis for view: app-ns2:view_protected_by_role\n'
        expected_2 += u'\t\tView url: role-included2/view_by_role/'
        expected_2 += u'\n\t\tView access is of type Public.'
        ViewAccess.objects.create(view='app-ns2:view_protected_by_role',
                                  type='pu')
        out = StringIO()
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())

    def test_decorator_view_access_object_app_type_SECURED(self):
        settings.__setattr__('SECURED', ['django_roles'])
        expected_1 = u'\n\tAnalyzing django_roles:'
        expected_1 += u'\n\t\tdjango_roles is SECURED type.'
        expected_2 = u'Analysis for view: app-ns2:view_protected_by_role\n'
        expected_2 += u'\t\tView url: role-included2/view_by_role/'
        expected_2 += u'\n\t\tView access is of type Public.'
        ViewAccess.objects.create(view='app-ns2:view_protected_by_role',
                                  type='pu')
        out = StringIO()
        call_command('checkviewaccess', stdout=out)
        settings.__delattr__('SECURED')
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())

    def test_mixin_no_view_access_object_app_type_None(self):
        expected_1 = u'\n\tAnalyzing django_roles:'
        expected_1 += u'\n\t\tdjango_roles has no type.'
        expected_2 = u'Analysis for view: app-ns2:mixin_class_view\n'
        expected_2 += u'\t\tView url: role-included2/mixin_class_view/'
        expected_2 += u'\n\t\t' + NONE_TYPE_DEFAULT
        out = StringIO()
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())

    def test_mixin_no_view_access_object_app_type_NOT_SECURED(self):
        settings.__setattr__('NOT_SECURED', ['django_roles'])
        expected_1 = u'\n\tAnalyzing django_roles:'
        expected_1 += u'\n\t\tdjango_roles is NOT_SECURED type.'
        expected_2 = u'Analysis for view: app-ns2:mixin_class_view\n'
        expected_2 += u'\t\tView url: role-included2/mixin_class_view/'
        expected_2 += u'\n\t\t' + NOT_SECURED_DEFAULT
        out = StringIO()
        call_command('checkviewaccess', stdout=out)
        settings.__delattr__('NOT_SECURED')
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())

    def test_mixin_no_view_access_object_app_type_SECURED(self):
        settings.__setattr__('SECURED', ['django_roles'])
        expected_1 = u'\n\tAnalyzing django_roles:'
        expected_1 += u'\n\t\tdjango_roles is SECURED type.'
        expected_2 = u'Analysis for view: app-ns2:mixin_class_view\n'
        expected_2 += u'\t\tView url: role-included2/mixin_class_view/'
        expected_2 += u'\n\t\t'
        out = StringIO()
        call_command('checkviewaccess', stdout=out)
        settings.__delattr__('SECURED')
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())

    def test_mixin_no_view_access_object_app_type_PUBLIC(self):
        settings.__setattr__('PUBLIC', ['django_roles'])
        expected_1 = u'\n\tAnalyzing django_roles:'
        expected_1 += u'\n\t\tdjango_roles is PUBLIC type.'
        expected_2 = u'Analysis for view: app-ns2:mixin_class_view\n'
        expected_2 += u'\t\tView url: role-included2/mixin_class_view/'
        expected_2 += u'\n\t\t'
        out = StringIO()
        call_command('checkviewaccess', stdout=out)
        settings.__delattr__('PUBLIC')
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())

    def test_mixin_view_access_object_app_type_None(self):
        expected_1 = u'\n\tAnalyzing django_roles:'
        expected_1 += u'\n\t\tdjango_roles has no type.'
        expected_2 = u'Analysis for view: app-ns2:mixin_class_view\n'
        expected_2 += u'\t\tView url: role-included2/mixin_class_view/'
        expected_2 += u'\n\t\tView access is of type Public.'
        ViewAccess.objects.create(view='app-ns2:mixin_class_view',
                                  type='pu')
        out = StringIO()
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())

    def test_mixin_view_access_object_app_type_SECURED(self):
        settings.__setattr__('SECURED', ['django_roles'])
        expected_1 = u'\n\tAnalyzing django_roles:'
        expected_1 += u'\n\t\tdjango_roles is SECURED type.'
        expected_2 = u'Analysis for view: app-ns2:view_protected_by_role\n'
        expected_2 += u'\t\tView url: role-included2/view_by_role/'
        expected_2 += u'\n\t\tView access is of type Public.'
        ViewAccess.objects.create(view='app-ns2:view_protected_by_role',
                                  type='pu')
        out = StringIO()
        call_command('checkviewaccess', stdout=out)
        settings.__delattr__('SECURED')
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())

    @modify_settings(MIDDLEWARE={
        'append': 'django_roles_access.middleware.RolesMiddleware'
    })
    def test_site_active_no_view_access_object_app_type_None(self):
        expected_1 = u'\n\tAnalyzing django_roles:'
        expected_1 += u'\n\t\tdjango_roles has no type.'
        expected_2 = u'Analysis for view: app-ns2:middleware_view_func\n'
        expected_2 += u'\t\tView url: role-included2/middleware_view_func/'
        expected_2 += u'\n\t\t' + NONE_TYPE_DEFAULT
        out = StringIO()
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())

    @modify_settings(MIDDLEWARE={
        'append': 'django_roles_access.middleware.RolesMiddleware'
    })
    def test_site_active_no_view_access_object_app_type_NOT_SECURED(self):
        settings.__setattr__('NOT_SECURED', ['django_roles'])
        expected_1 = u'\n\tAnalyzing django_roles:'
        expected_1 += u'\n\t\tdjango_roles is NOT_SECURED type.'
        expected_2 = u'Analysis for view: app-ns2:middleware_view_func\n'
        expected_2 += u'\t\tView url: role-included2/middleware_view_func/'
        expected_2 += u'\n\t\t' + NOT_SECURED_DEFAULT
        out = StringIO()
        call_command('checkviewaccess', stdout=out)
        settings.__delattr__('NOT_SECURED')
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())

    @modify_settings(MIDDLEWARE={
        'append': 'django_roles_access.middleware.RolesMiddleware'
    })
    def test_site_active_no_view_access_object_app_type_SECURED(self):
        settings.__setattr__('SECURED', ['django_roles'])
        expected_1 = u'\n\tAnalyzing django_roles:'
        expected_1 += u'\n\t\tdjango_roles is SECURED type.'
        expected_2 = u'Analysis for view: app-ns2:middleware_view_func\n'
        expected_2 += u'\t\tView url: role-included2/middleware_view_func/'
        expected_2 += u'\n\t\t'
        out = StringIO()
        call_command('checkviewaccess', stdout=out)
        settings.__delattr__('SECURED')
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())

    @modify_settings(MIDDLEWARE={
        'append': 'django_roles_access.middleware.RolesMiddleware'
    })
    def test_site_active_no_view_access_object_app_type_PUBLIC(self):
        settings.__setattr__('PUBLIC', ['django_roles'])
        expected_1 = u'\n\tAnalyzing django_roles:'
        expected_1 += u'\n\t\tdjango_roles is PUBLIC type.'
        expected_2 = u'Analysis for view: app-ns2:middleware_view_func\n'
        expected_2 += u'\t\tView url: role-included2/middleware_view_func/'
        expected_2 += u'\n\t\t'
        out = StringIO()
        call_command('checkviewaccess', stdout=out)
        settings.__delattr__('PUBLIC')
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())

    @modify_settings(MIDDLEWARE={
        'append': 'django_roles_access.middleware.RolesMiddleware'
    })
    def test_site_active_view_access_object_app_type_None(self):
        expected_1 = u'\n\tAnalyzing django_roles:'
        expected_1 += u'\n\t\tdjango_roles has no type.'
        expected_2 = u'Analysis for view: app-ns2:middleware_view_func\n'
        expected_2 += u'\t\tView url: role-included2/middleware_view_func/'
        expected_2 += u'\n\t\tView access is of type Public.'
        ViewAccess.objects.create(view='app-ns2:middleware_view_func',
                                  type='pu')
        out = StringIO()
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())

    @modify_settings(MIDDLEWARE={
        'append': 'django_roles_access.middleware.RolesMiddleware'
    })
    def test_site_active_view_access_object_app_type_NOT_SECURED(self):
        settings.__setattr__('NOT_SECURED', ['django_roles'])
        expected_1 = u'\n\tAnalyzing django_roles:'
        expected_1 += u'\n\t\tdjango_roles is NOT_SECURED type.'
        expected_2 = u'Analysis for view: app-ns2:middleware_view_func\n'
        expected_2 += u'\t\tView url: role-included2/middleware_view_func/'
        expected_2 += u'\n\t\tView access is of type Public.'
        ViewAccess.objects.create(view='app-ns2:middleware_view_func',
                                  type='pu')
        out = StringIO()
        call_command('checkviewaccess', stdout=out)
        settings.__delattr__('NOT_SECURED')
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())

    @modify_settings(MIDDLEWARE={
        'append': 'django_roles_access.middleware.RolesMiddleware'
    })
    def test_site_active_view_access_object_app_type_SECURED(self):
        settings.__setattr__('SECURED', ['django_roles'])
        expected_1 = u'\n\tAnalyzing django_roles:'
        expected_1 += u'\n\t\tdjango_roles is SECURED type.'
        expected_2 = u'Analysis for view: app-ns2:middleware_view_func\n'
        expected_2 += u'\t\tView url: role-included2/middleware_view_func/'
        expected_2 += u'\n\t\tView access is of type By role.'
        expected_2 += u'\n\t\t\tRoles with access: role-1, role-2'
        role_1, created = Group.objects.get_or_create(name='role-1')
        role_2, created = Group.objects.get_or_create(name='role-2')
        view_access = ViewAccess.objects.create(
            view='app-ns2:middleware_view_func',
            type='br')
        view_access.roles.add(role_1)
        view_access.roles.add(role_2)
        view_access.save()
        out = StringIO()
        call_command('checkviewaccess', stdout=out)
        settings.__delattr__('SECURED')
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())

    @modify_settings(MIDDLEWARE={
        'append': 'django_roles_access.middleware.RolesMiddleware'
    })
    def test_site_active_view_access_object_app_type_PUBLIC(self):
        settings.__setattr__('PUBLIC', ['django_roles'])
        expected_1 = u'\n\tAnalyzing django_roles:'
        expected_1 += u'\n\t\tdjango_roles is PUBLIC type.'
        expected_2 = u'Analysis for view: app-ns2:middleware_view_func\n'
        expected_2 += u'\t\tView url: role-included2/middleware_view_func/'
        expected_2 += u'\n\t\tView access is of type Authorized.'
        ViewAccess.objects.create(view='app-ns2:middleware_view_func',
                                  type='au')
        out = StringIO()
        call_command('checkviewaccess', stdout=out)
        settings.__delattr__('PUBLIC')
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())

