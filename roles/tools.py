from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.urls import resolve
from django.db.models import Q

from roles.models import ViewAccess


def get_view_access(request):
    """
    Check if given an application and a view have an access configurations:
    an object of :class:`roles.models.ViewAccess`. Also check if given user
    has a role with permission to access the view.

    :param request:
    :return: True if user have access. Or raise PermissionDenied.
    """
    user = request.user
    current_url = resolve(request.path_info)
    view_name = current_url.url_name
    namespace = current_url.namespace

    view_access = ViewAccess.objects.filter(
        Q(view=u'{}:{}'.format(namespace, view_name)) |
        Q(view=view_name)).first()
    if view_access:
        if view_access.type == 'pu':
            return True
        elif view_access.type == 'au':
            if user.is_authenticated:
                return True
            else:
                raise PermissionDenied
        elif view_access.type == 'br':
            if user.is_authenticated:
                access = list(set(user.groups.all()) &
                              set(view_access.roles.all()))
                if access:
                    return True
                else:
                    raise PermissionDenied
            else:
                raise PermissionDenied


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

    # If view has an access configuration, this takes precedence over
    # the classification of the application
    if get_view_access(request):
        return True

    # Check for public applications
    if app_name in setting_dictionary['PUBLIC']:
        return True
    if app_name in setting_dictionary['SECURED']:
        if not request.user.is_authenticated:
            return False
    return True
