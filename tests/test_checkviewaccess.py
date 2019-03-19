from django.conf import settings
from django.contrib.auth.models import Group
try:
    from django.utils.six import StringIO
except:
    from io import StringIO

from django_roles_access.models import ViewAccess

try:
    from unittest.mock import Mock, patch, MagicMock, ANY
except:
    from mock import Mock, patch, ANY
from unittest.case import TestCase as UnitTestCase

from django.core.management import call_command
from django.test import TestCase, modify_settings
from django_roles_access.utils import (NONE_TYPE_DEFAULT, NOT_SECURED_DEFAULT,
                                       SECURED_DEFAULT, PUBLIC_DEFAULT,
                                       APP_NAME_FOR_NONE)


@patch('django_roles_access.management.commands.checkviewaccess.import_module')
@patch('django_roles_access.management.commands.checkviewaccess.settings')
class UnitTestCheckViewAccess(UnitTestCase):

    def setUp(self):
        self.root_urlconf = Mock()

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

    def test_import_module_is_called(
            self, mock_settings, mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        call_command('checkviewaccess')
        assert mock_import_module.called

    def test_import_module_is_called_once(
            self, mock_settings, mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        call_command('checkviewaccess')
        self.assertEqual(mock_import_module.call_count, 1)

    def test_import_module_is_called_once_with(
            self, mock_settings, mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        call_command('checkviewaccess')
        mock_import_module.assert_called_once_with(self.root_urlconf)

    @patch('django_roles_access.management.commands.checkviewaccess.walk_site_url')
    def test_walk_site_url_is_called(
            self, mock_walk_site_url, mock_settings, mock_import_module
    ):
        mock_import_module.urlpatterns = 'fake-url-pattern'
        call_command('checkviewaccess')
        assert mock_walk_site_url.called

    @patch('django_roles_access.management.commands.checkviewaccess.walk_site_url')
    def test_walk_site_url_is_called_once(
            self, mock_walk_site_url, mock_settings, mock_import_module
    ):
        mock_import_module.urlpatterns = 'fake-url-pattern'
        call_command('checkviewaccess')
        self.assertEqual(mock_walk_site_url.call_count, 1)

    @patch('django_roles_access.management.commands.checkviewaccess.walk_site_url')
    def test_walk_site_url_is_called_once_with(
            self, mock_walk_site_url, mock_settings, mock_import_module
    ):
        urlpatterns = Mock()
        urlpatterns.urlpatterns = 'fake-urlpatterns'
        mock_import_module.return_value = urlpatterns
        call_command('checkviewaccess')
        mock_walk_site_url.assert_called_once_with('fake-urlpatterns')

    @patch('django_roles_access.management.commands.checkviewaccess.get_views_by_app')
    def test_get_views_by_app_is_called(
            self, mock_get_views_by_app, mock_settings, mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        call_command('checkviewaccess')
        assert mock_get_views_by_app.called

    @patch('django_roles_access.management.commands.checkviewaccess.get_views_by_app')
    def test_get_views_by_app_is_called_once(
            self, mock_get_views_by_app, mock_settings, mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        call_command('checkviewaccess')
        self.assertEqual(mock_get_views_by_app.call_count, 1)

    @patch('django_roles_access.management.commands.checkviewaccess.walk_site_url')
    @patch('django_roles_access.management.commands.checkviewaccess.get_views_by_app')
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
        expected_text = u'Django roles active for site: True.'
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_text, out.getvalue())

    def test_middleware_is_not_active_and_site_active_is_false(
            self, mock_settings, mock_import_module
    ):
        mock_settings.MIDDLEWARE = ['fake-middleware',
                                    'other-fake-middleware']
        mock_settings.ROOT_URLCONF = self.root_urlconf
        out = StringIO()
        expected_text = u'Django roles active for site: False.'
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
        self.assertEqual(mock_print_view_analysis.call_count, 1)

    @patch('django_roles_access.management.commands.checkviewaccess.get_views_by_app')
    @patch('django_roles_access.management.commands.checkviewaccess.'
           'view_access_analyzer')
    @patch('django_roles_access.management.commands.checkviewaccess'
           '.print_view_analysis')
    def test_print_view_analyzer_is_called_1_times_with_param(
            self, mock_print_view_analysis,
            mock_view_access_analyzer, mock_view_by_app, mock_settings,
            mock_import_module
    ):
        mock_settings.ROOT_URLCONF = self.root_urlconf
        mock_view_by_app.return_value = {'fake-app':
                                         [('/fake1/', 'fake-callback-1',
                                           'fake-view')]}
        mock_view_access_analyzer.return_value = u'fake-analysis'
        call_command('checkviewaccess')
        mock_print_view_analysis.assert_called_once_with(ANY, ANY,
                                                         u'fake-analysis')


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

    SECURED_DEFAULT = u''

    PUBLIC_DEFAULT = u''

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
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())
        settings.__delattr__('SECURED')

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
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())
        settings.__delattr__('NOT_SECURED')

    def test_decorator_no_view_access_object_app_type_SECURED(self):
        settings.__setattr__('SECURED', ['django_roles'])
        expected_1 = u'\n\tAnalyzing django_roles:'
        expected_1 += u'\n\t\tdjango_roles is SECURED type.'
        expected_2 = u'Analysis for view: app-ns2:view_protected_by_role\n'
        expected_2 += u'\t\tView url: role-included2/view_by_role/'
        expected_2 += u'\n\t\t' + SECURED_DEFAULT
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
        expected_2 += u'\n\t\t' + PUBLIC_DEFAULT
        out = StringIO()
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())
        settings.__delattr__('PUBLIC')

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
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())
        settings.__delattr__('SECURED')

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
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())
        settings.__delattr__('NOT_SECURED')

    def test_mixin_no_view_access_object_app_type_SECURED(self):
        settings.__setattr__('SECURED', ['django_roles'])
        expected_1 = u'\n\tAnalyzing django_roles:'
        expected_1 += u'\n\t\tdjango_roles is SECURED type.'
        expected_2 = u'Analysis for view: app-ns2:mixin_class_view\n'
        expected_2 += u'\t\tView url: role-included2/mixin_class_view/'
        expected_2 += u'\n\t\t' + SECURED_DEFAULT
        out = StringIO()
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())
        settings.__delattr__('SECURED')

    def test_mixin_no_view_access_object_app_type_PUBLIC(self):
        settings.__setattr__('PUBLIC', ['django_roles'])
        expected_1 = u'\n\tAnalyzing django_roles:'
        expected_1 += u'\n\t\tdjango_roles is PUBLIC type.'
        expected_2 = u'Analysis for view: app-ns2:mixin_class_view\n'
        expected_2 += u'\t\tView url: role-included2/mixin_class_view/'
        expected_2 += u'\n\t\t' + PUBLIC_DEFAULT
        out = StringIO()
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())
        settings.__delattr__('PUBLIC')

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
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())
        settings.__delattr__('SECURED')

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
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())
        settings.__delattr__('NOT_SECURED')

    @modify_settings(MIDDLEWARE={
        'append': 'django_roles_access.middleware.RolesMiddleware'
    })
    def test_site_active_no_view_access_object_app_type_SECURED(self):
        settings.__setattr__('SECURED', ['django_roles'])
        expected_1 = u'\n\tAnalyzing django_roles:'
        expected_1 += u'\n\t\tdjango_roles is SECURED type.'
        expected_2 = u'Analysis for view: app-ns2:middleware_view_func\n'
        expected_2 += u'\t\tView url: role-included2/middleware_view_func/'
        expected_2 += u'\n\t\t' + SECURED_DEFAULT
        out = StringIO()
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())
        settings.__delattr__('SECURED')

    @modify_settings(MIDDLEWARE={
        'append': 'django_roles_access.middleware.RolesMiddleware'
    })
    def test_site_active_no_view_access_object_app_type_PUBLIC(self):
        settings.__setattr__('PUBLIC', ['django_roles'])
        expected_1 = u'\n\tAnalyzing django_roles:'
        expected_1 += u'\n\t\tdjango_roles is PUBLIC type.'
        expected_2 = u'Analysis for view: app-ns2:middleware_view_func\n'
        expected_2 += u'\t\tView url: role-included2/middleware_view_func/'
        expected_2 += u'\n\t\t' + PUBLIC_DEFAULT
        out = StringIO()
        call_command('checkviewaccess', stdout=out)
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())
        settings.__delattr__('PUBLIC')

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
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())
        settings.__delattr__('NOT_SECURED')

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
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())
        settings.__delattr__('SECURED')

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
        self.assertIn(expected_1, out.getvalue())
        self.assertIn(expected_2, out.getvalue())
        settings.__delattr__('PUBLIC')

