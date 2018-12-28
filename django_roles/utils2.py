"""
The code in this page make django-roles fail with Django 1.x versions.

Django 1.11 use url() instead of path(). Do the same service for both?
If not, better leave it for Django 2 and in Django 1.11 installations to
be ignored.
Problem:

URLPattern, URLResolver: Do not exist in Django 1.x versions

Cause:

Django 1.x versions use *url* for URLConf. Django 2.x use *path*.
"""
#: TODO: Are this function realy needed?
from importlib import import_module
from django.urls import URLPattern, URLResolver
from django.conf import settings


def get_site_views():
    """
    This function

    1 Get *main urlpatterns* for the site. This is starting point to get all
      possible views that can be accessed by a user under the conception that
      if there is no URL pointing the view, there is no way to access a view.
    2 *main urlpatterns* can be a list of URLResolver and/or URLPattern
      objects.
    3 An URLResolver can be a list of URLResolver and/or URLPattern objects.

    URLResolver provides:
    a app_name
    b namespace

    URLPattern provides:
    a name
    b lookup_str
    c pattern

    Debe haber una función que reciba un URLResolver y recorra su contenido,
    1 si un elemento es un URLResolver se vuelve a llamar a si misma (recursivo)
      con el URLResolver
    2 Si el elemento es un URLPattern, se obtienen los datos, se concatena el
      nombre de la aplicación y se suma a la lista que se va devolviendo.

    :return: A tuple: (path, name, view):
    * *path*: The path to be verified: /polls/<...>/result
    * *name*: Name of the view: polls:result
    * *view*: Class o function called when path is hit.
    """
    # Main urlpatterns for the site:
    url_patterns = import_module(settings.ROOT_URLCONF).urlpatterns
    for url in url_patterns:
        if isinstance(url, URLPattern):
            print(url)
        else:
            print(url.url_patterns)
    return []


def get_site_urls(url_patterns):
    result = []
    for url in url_patterns:
        if isinstance(url, URLResolver):
            result.extend({url.app_name: get_site_urls(url.url_patterns)})
        elif isinstance(url, URLPattern):
            result.append(url)
    return result


def get_url_app_view():
    result = []
    url_patterns = import_module(settings.ROOT_URLCONF).urlpatterns
    urls = list(set(get_site_urls(url_patterns)))
    for url in urls:
        if isinstance(url, dict):
            for key_, values in url:
                for value in values:
                    result.append(('{}:{}'.format(key_, value),
                                  value.lookup_str, value.pattern))
        else:
            print(url)
            # result.append((url.name, url.lookup_str, url.pattern))
    return result
