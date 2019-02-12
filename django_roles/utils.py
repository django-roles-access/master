"""
Code used by checkviewaccess management command
"""
from django.conf import settings
from django.utils.translation import ugettext as _


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
