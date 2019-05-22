from django.conf import settings
from django.http import HttpResponseForbidden, HttpResponseRedirect
try:
    from django.utils.translation import ugettex as _
except:
    from django.utils.translation import gettext as _
from django.urls import resolve

from django_roles_access.models import ViewAccess

DEFAULT_FORBIDDEN_MESSAGE = _(u'<h1>403 Forbidden</h1>')


def get_view_access(request):
    """
    Check access if exist a ViewAccess object for the view being processed.

    A ViewAccess object is linked to present view when current namespace and
    view name are the value of *view* attribute of the ViewAccess object. Can
    be only one ViewAccess object for each namespace and view name. If no
    namespace is used, application name is used instead as Django default
    behavior. This also means for Django < 2.0 the attribute app_name is
    required in URLConf (Django > 2.0 has this requirement).

    If exist a ViewAccess object linked to present view, security checks are
    done to conclude if request user have access or not. In case request user
    do not have access, PermissionDenied is raised.

    :return: True if user have access. Or raise PermissionDenied.
    """
    user = request.user
    current_url = resolve(request.path_info)
    view_name = current_url.view_name

    view_access = ViewAccess.objects.filter(view=view_name).first()
    if view_access:
        if view_access.type == 'pu':
            return True
        elif view_access.type == 'au':
            if user.is_authenticated:
                return True
            else:
                return False
        elif view_access.type == 'br':
            if user.is_authenticated:
                access = list(set(user.groups.all()) &
                              set(view_access.roles.all()))
                if access:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return None


def get_setting_dictionary():
    """
    Return django-roles settings variable or None.

    :return: Dictionary with three keys: NOT_SECURE, PUBLIC, SECURE with their
             settings values or None.
    """
    settings_dictionary = {}

    try:
        settings_dictionary['NOT_SECURED'] = settings.NOT_SECURED
    except AttributeError:
        settings_dictionary['NOT_SECURED'] = []

    try:
        settings_dictionary['PUBLIC'] = settings.PUBLIC
    except AttributeError:
        settings_dictionary['PUBLIC'] = []

    try:
        settings_dictionary['SECURED'] = settings.SECURED
    except AttributeError:
        settings_dictionary['SECURED'] = []

    try:
        settings_dictionary['DISABLED'] = settings.DISABLED
    except AttributeError:
        settings_dictionary['DISABLED'] = []

    return settings_dictionary


def check_access_by_role(request):
    """
    Given a request to access a view the function check if user (logged or
    not) can access required view.

    :param request: :class:`django.http.HttpRequest`
    :return: True if can access the view. False in other case.
    """
    current_url = resolve(request.path_info)
    app_name = current_url.app_name
    setting_dictionary = get_setting_dictionary()

    # NOT_SECURED applications are ignored
    if app_name in setting_dictionary['NOT_SECURED']:
        return True
    # DISABLED applications are denied
    if app_name in setting_dictionary['DISABLED']:
        return False
    # If view has an access configuration, this takes precedence over
    # the classification of the application
    view_access = get_view_access(request)
    if view_access is not None:
        return view_access
    # Check for public applications
    if app_name in setting_dictionary['PUBLIC']:
        return True
    if app_name in setting_dictionary['SECURED']:
        if not request.user.is_authenticated:
            return False
    return True


def get_app_type(app_name):
    for key, val in get_setting_dictionary().items():
        if app_name in val:
            return key
    return None


def get_forbidden_message():
    if hasattr(settings, 'DJANGO_ROLES_ACCESS_FORBIDDEN_MESSAGE'):
        return settings.DJANGO_ROLES_ACCESS_FORBIDDEN_MESSAGE
    return DEFAULT_FORBIDDEN_MESSAGE


def get_no_access_response():
    if hasattr(settings, 'DJANGO_ROLES_ACCESS_REDIRECT'):
        if settings.DJANGO_ROLES_ACCESS_REDIRECT:
            return HttpResponseRedirect(settings.LOGIN_URL)
    if hasattr(settings, 'DJANGO_ROLES_ACCESS_FORBIDDEN_MESSAGE'):
        return HttpResponseForbidden(
            settings.DJANGO_ROLES_ACCESS_FORBIDDEN_MESSAGE)
    return HttpResponseForbidden(DEFAULT_FORBIDDEN_MESSAGE)
