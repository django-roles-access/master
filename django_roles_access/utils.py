"""
Code used by checkviewaccess management _output
"""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
try:
    from django.utils.translation import gettext as _
except:
    from django.utils.translation import ugettext as _

from django_roles_access.models import ViewAccess

User = get_user_model()
APP_NAME_FOR_NONE = _(u'Undefined app')

NOT_SECURED_DEFAULT = _(u'WARNING: View belongs to an application of type '
                        u'"NOT_SECURED". No access is checked at all.')

DISABLED_DEFAULT = _(u'WARNING: Application is DISABLED. All access are '
                     u'forbidden')

SECURED_DEFAULT = _(u'No security configured for the view (ViewAccess '
                    u'object) and application type is "SECURED". User is '
                    u'required to be authenticated to access the view.')

PUBLIC_DEFAULT = _(u'No security configured for the view (ViewAccess object)'
                   u' and application type is "PUBLIC". Anonymous user can'
                   u' access the view.')

NONE_TYPE_DEFAULT = _(u'ERROR: Django roles access middleware is active; or '
                      u'view is protected with Django roles decorator or mixin,'
                      u' and has no application or application has no type. '
                      u'There are no View Access object for the view. Is not '
                      u'possible to determine behavior for access view. Access'
                      u' to view is determined by view implementation.')


def walk_site_url(_url_patterns, recursive_url='',
                  view_name=None, app_name=None):
    result = []
    for url in _url_patterns:
        if hasattr(url, 'pattern'):
            # Running With Django 2
            pattern = str(url.pattern)
        else:
            # Running with Django 1
            pattern = str(url.regex.pattern)
        pattern = pattern.strip('^').strip('$')  # For better presentation
        if hasattr(url, 'url_patterns'):
            # When url object has 'url_patterns' attribute means is a Resolver
            if url.namespace:
                if view_name:
                    new_view_name = view_name + ":" + url.namespace
                else:
                    new_view_name = url.namespace
            else:
                new_view_name = None
            result.extend(walk_site_url(url.url_patterns,
                                        recursive_url + pattern,
                                        new_view_name, url.app_name))
        else:
            if view_name:
                new_view_name = view_name + ":" + url.name
            else:
                new_view_name = url.name
            result.append((recursive_url + pattern, url.callback,
                           new_view_name, app_name))

    return result


def get_views_by_app(site_urls):
    installed_apps = settings.INSTALLED_APPS
    result = {key: [] for key in installed_apps}
    for site_url in site_urls:
        try:
            url, callback, view_name, app_name = site_url
        except:
            raise TypeError
        if not app_name:
            app_name = APP_NAME_FOR_NONE
        try:
            result[app_name].append((url, callback, view_name))
        except KeyError:
            result[app_name] = [(url, callback, view_name)]
    return result


def get_view_analyze_report(app_type):
    if app_type == 'NOT_SECURED':
        return u'\t' + NOT_SECURED_DEFAULT
    elif app_type == 'DISABLED':
        return u'\t' + DISABLED_DEFAULT
    elif app_type == 'SECURED':
        return u'\t' + SECURED_DEFAULT
    elif app_type == 'PUBLIC':
        return u'\t' + PUBLIC_DEFAULT
    else:
        return u'\t' + NONE_TYPE_DEFAULT


def check_django_roles_is_used(view):
    if hasattr(view, 'access_by_role'):
        return True
    elif 'dispatch' in dir(view):
        if hasattr(view.dispatch, 'access_by_role'):
            return True
    return False


def analyze_by_role(view_access):
    result = u''
    if view_access.type == 'br':
        if view_access.roles.count() != 0:
            result = _(u'Roles with access: ')
            for role in view_access.roles.all():
                result += role.name + u', '
            result = result[:-2]
        else:
            result = _(u'ERROR: No roles configured to access de view.')
    return result


def view_access_analyzer(app_type, callback, view_name, site_active):
    result = _(u'No Django roles access tool used. Access to view depends on '
               u'its implementation.')
    if app_type in ['NOT_SECURED', 'DISABLED']:
        return get_view_analyze_report(app_type)
    view_access = ViewAccess.objects.filter(view=view_name).first()
    if site_active:
        if view_access:
            view_access_type = dict(ViewAccess.ACCESS_TYPES)[view_access.type]
            result = _(u'View access is of type {}.'.format(view_access_type))
            result += analyze_by_role(view_access)
        else:
            result = get_view_analyze_report(app_type)
    else:
        if check_django_roles_is_used(callback):
            if view_access:
                view_access_type = \
                    dict(ViewAccess.ACCESS_TYPES)[view_access.type]
                result = _(
                    u'View access is of type {}.'.format(view_access_type))
                result += analyze_by_role(view_access)
            else:
                result = get_view_analyze_report(app_type)
        else:
            if view_access:
                result = _(u'ERROR: View access object exist for the view, '
                           u'but no Django role access tool is used: neither '
                           u'decorator, mixin, or middleware.')
    return result


class OutputReport(object):

    HEADER = _(u'Start checking views access.\nStart gathering information.')
    MIDDLEWARE_STATUS = _('Django roles access middleware is active:')
    END_HEADER = _(u'Finish gathering information.')
    CONSOLE = 'console'
    CSV = 'csv'
    CSV_COLUMNS = _(u'App Name,Type,View Name,Url,Status,Status description')

    def __init__(self, stdout, style):
        self.stdout = stdout
        self.style = style
        self._format = 'console'
        self._row = u''

    def set_format(self, _format):
        self._format = _format

    def add_to_row(self, data):
        self._row += data

    def write(self, text):
        self.stdout.write(self.style.SUCCESS(text))

    def write_header(self):
        if self._format == self.CONSOLE:
            self.write(self.HEADER)
        elif self._format == self.CSV:
            self.write(_(u'Reported: {}'.format(timezone.now())))

    def write_middleware_status(self, status):
        output = self.MIDDLEWARE_STATUS + ' {}.\n'.format(status)
        self.stdout.write(self.style.SUCCESS(output))

    def write_end_of_head(self):
        if self._format == self.CONSOLE:
            output = self.END_HEADER
        else:  # self._format == self.CSV:
            output = self.CSV_COLUMNS
        self.write(output)

    def process_application_data(self, app_name, app_type, view_list):
        output = _(u'\tAnalyzing: {}\n'.format(app_name))
        _app_type = app_type
        if app_type is None:
            output += _(u'\t\t{} has no type.'.format(app_name, app_type))
            _app_type = _('no type')
        else:
            output += _(u'\t\t{} is {} type.'.format(app_name, app_type))
        if len(view_list) == 0:
            output += _(u'\t\t{} does not have configured views.'.format(
                app_name))
            _app_type += ',,,,'
        if self._format == self.CONSOLE:
            self.write(output)
        elif self._format == self.CSV:
            self.add_to_row('{},{},'.format(app_name, _app_type))

    def process_view_data(self, view_name, url):
        if self._format == self.CONSOLE:
            _output = _(u'\n\t\tAnalysis for view: {}'.format(view_name))
            _output += _(u'\n\t\tView url: {}'.format(url))
            self.write(_output)
        elif self._format == self.CSV:
            self.add_to_row('{},{},'.format(view_name, url))

    def write_view_access_analyzer(self, text):
        if self._format == self.CONSOLE:
            if 'ERROR:' in text:
                self.stdout.write(self.style.ERROR('\t\t' + text))
            elif 'WARNING:' in text:
                self.stdout.write(self.style.WARNING('\t\t' + text))
            else:
                self.write('\t\t' + text)
        elif self._format == self.CSV:
            _row = self._row.split(',')
            if 'ERROR:' in text:
                self.add_to_row(u'Error,{}\n'.format(text.split('ERROR: ')[1]))
                _output = self.style.ERROR(self._row)
            elif 'WARNING:' in text:
                self.add_to_row(u'Warning,{}\n'.format(
                    text.split('WARNING: ')[1]))
                _output = self.style.WARNING(self._row)
            else:
                self.add_to_row(u'Normal,{}\n'.format(text))
                _output = self.style.SUCCESS(self._row)
            self.stdout.write(_output)
            # Delete view information to start cycle again.
            # only app_name and app_type are left.
            self._row = _row[0] + ',' + _row[1] + ','

    def close_application_data(self, app_name):
        if self._format == self.CONSOLE:
            _output = _(u'\tFinish analyzing {}.').format(app_name)
            self.write(_output)
        elif self._format == self.CSV:
            self._row = u''

    def write_footer(self):
        if self._format == self.CONSOLE:
            _output = _(u'End checking view access.')
            self.write(_output)
        elif self._format == self.CSV:
            self._row = u'\n'
