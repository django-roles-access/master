"""
Code used by checkviewaccess management command
"""
from django.conf import settings
from importlib import import_module
#
# url = import_module(settings.ROOT_URLCONF).urlpatterns

try:
    from django.urls.resolvers import URLResolver
except:
    from django.core.urlresolvers import RegexURLResolver


def walk_site_url(urlpattern):
    result = []
    for url in urlpattern:
        result.append((url.regex.pattern, url.callback))
    return result


def walk_url_conf(urlpatterns, namespace=''):
    for element in urlpatterns:
        django_version = False
        try:
            django_version = isinstance(element, URLResolver)
        except:
            django_version = isinstance(element, RegexURLResolver)
        if django_version:
            walk_url_conf(element.url_patterns, namespace +
                          element.regex.pattern)
        else:
            print(element.name)
            print(namespace + element.regex.pattern)
            # print(element.callback)
            if hasattr(element.callback, 'access_by_role'):
                print("Protected View")