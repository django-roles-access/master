"""
Code used by checkviewaccess management command
"""
from django.conf import settings
from django.contrib.auth import get_user_model
try:
    from django.utils.translation import gettext as _
except:
    from django.utils.translation import ugettext as _

from django_roles_access.models import ViewAccess

User = get_user_model()
APP_NAME_FOR_NONE = _(u'Undefined app')

NOT_SECURED_DEFAULT = _(u'WARNING: View has no security configured '
                        u'(ViewAccess) and application type is "NOT_SECURED".'
                        u' No access is checked at all.')

SECURED_DEFAULT = _(u'No security configured for the view (ViewAccess '
                    u'object) and application type is "SECURED". User is '
                    u'required to be authenticated to access the view.')

PUBLIC_DEFAULT = _(u'No security configured for the view (ViewAccess object)'
                   u' and application type is "PUBLIC". Anonymous user can'
                   u' access the view.')

NONE_TYPE_DEFAULT = _(u'ERROR: Django roles middleware is active; or view'
                      u' is protected with Django roles decorator or mixin,'
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
            result = _(u'\n\t\t\tRoles with access: ')
            for role in view_access.roles.all():
                result += role.name + u', '
            result = result[:-2]
        else:
            result = _(u'\n\t\t\tERROR: No roles configured to access de view.')
    return result


def view_access_analyzer(app_type, callback, view_name, site_active):
    result = _(u'\tNo Django roles tool used. Access to view depends on '
               u'its implementation.')
    view_access = ViewAccess.objects.filter(view=view_name).first()
    if site_active:
        if view_access:
            view_access_type = dict(ViewAccess.ACCESS_TYPES)[view_access.type]
            result = _(u'\tView access is of type {}.'.format(view_access_type))
            result += analyze_by_role(view_access)
        else:
            result = get_view_analyze_report(app_type)
    else:
        if check_django_roles_is_used(callback):
            if view_access:
                view_access_type = \
                    dict(ViewAccess.ACCESS_TYPES)[view_access.type]
                result = _(
                    u'\tView access is of type {}.'.format(view_access_type))
                result += analyze_by_role(view_access)
            else:
                result = get_view_analyze_report(app_type)
        else:
            if view_access:
                result = _(u'\tERROR: View access object exist for the view, '
                           u'but no Django role tool is used: neither '
                           u'decorator, mixin, or middleware.')
    return result


def print_view_analysis(stdout, style, report):
    if 'ERROR' in report:
        stdout.write(style.ERROR('\t' + report))
    elif 'WARNING' in report:
        stdout.write(style.WARNING('\t' + report))
    else:
        stdout.write(style.SUCCESS('\t' + report))
