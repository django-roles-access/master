"""
Code used by checkviewaccess management command
"""
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.views import logout
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _


User = get_user_model()
APP_NAME_FOR_NONE = _(u'Undefined app')


def walk_site_url(_url_patterns, recursive_url='',
                  view_name=None, app_name=None):
    """

    :param _url_patterns:
    :param recursive_url:
    :param view_name:
    :param app_name:
    :return: A list of tuples: (url, callback view, foo:view_name, app_name)
    """
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
            if view_name:
                new_view_name = view_name + ":" + url.namespace
            else:
                new_view_name = url.namespace
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
    """

    :param site_urls:
    :return:
    """
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


def view_access_analyzer(url, callback, view_name):
    """
    Expected behavior:

    The function analyze the callback, **a function**, searching for:

    * Any ``django.contrib.auth.decorators``.


    :param url:
    :param callback:
    :param view_name:
    :return:
    If any ``django.contrib.auth.decorators`` is present it will be included
    in report.

    """
    #: request_anonymous


    #: request_1: Has user. Is loged. And is super user.
    super_user, created = User.objects.get_or_create(
        username='django_roles_superuser')
    if created:
        super_user.is_superuser = True
        super_user.save()

    request_1 = RequestFactory()
    # request_1.user = super_user

    request_1.user = AnonymousUser()

    def return_uri():
        return u'/'

    def return_path():
        return url

    request_1.build_absolute_uri = return_uri
    request_1.get_full_path = return_path

    # request_1.session = {}

    # # Session
    # middleware = SessionMiddleware()
    # middleware.process_request(request_1)
    # request_1.session.save()

    # logout(request_1)

    response = callback(request_1)
    print(response.content)
    return response


# def get_view_decorators(function):
#     functions = []
#     if not function:
#         return []
#     if isinstance(function, str):
#         return [function]
#     if not function.__closure__:
#         return [(function.__name__, function.__module__, function.__dict__)]
#     for cell in function.__closure__:
#         functions.extend(get_view_decorators(cell.cell_contents))
#     return [(function.__name__, function.__module__, function.__dict__)] \
#         + functions
    # result = []
    # if not function.__closure__:
    #     return [function.__name__]
    # else:
    #     for cell in function.__closure__:
    #         if cell.cell_contents:
    #             result.extend(get_view_decorators(cell.cell_contents))
    # return [function.__name__] + result
