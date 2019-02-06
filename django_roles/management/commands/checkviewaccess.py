# -*- coding: utf-8 -*-
"""
This test module will search for all site's urls and analyze their security
status.
"""
from unittest.case import TestCase
from django.core.management.base import BaseCommand, CommandError
try:
    from django.urls.resolvers import URLResolver
except:
    from django.core.urlresolvers import RegexURLResolver


def walk_url_conf(urlpatterns):
    for element in urlpatterns:
        django_version = False
        try:
            django_version = isinstance(element, URLResolver)
        except:
            django_version = isinstance(element, RegexURLResolver)
        if django_version:
            walk_url_conf(element.url_patterns)
        else:
            print(element.name)
            print(element.regex.pattern)
            print(element.callback)
            if hasattr(element.callback, 'access_by_role'):
                print("Protected View")


class Command(BaseCommand):
    help = 'Manage command apptask'

    # def add_arguments(self, parser):
    #     """
    #     The command can receive arguments. They have to be
    #     declared in add_arguments method.
    #     """
    #     parser.add_argument('ids', nargs='+', type=int)

    def handle(self, *args, **options):
        """
        This method implements the manage.py command
        """
        from django.conf import settings
        from importlib import import_module
        url = import_module(settings.ROOT_URLCONF).urlpatterns
        walk_url_conf(url)
        # for element_id in options['ids']:
        #     try:
        #         my_data = MyData.objects.get(id=element_id)
        #     except MyData.DoesNotExist:
        #         raise CommandError('Poll "%s" does not exist' % poll_id)
        #
        #     my_data.some_attribute = False
        #     my_data.save()

        # Use this way to print output.
        self.stdout.write(self.style.SUCCESS('Check Site Views access '
                                             'configuration.'))


class AnalyzeSiteSecurity(TestCase):
    """
    The main class for analyzing site security.

    In this context *site security* means:
    * All site's urls have been recover and analyzed.
    * The uls analyze is: for the called view:
      a Recover view's security from :class:`roles.models.SecurityAccess`.
      b If there is no object related with the view:
        + Check for application configuration:
          a If application si **public**. Is OK.
          b If application is **no public**: TEST if login is required for the
            view. In **no public** application the default behavior is to
            require login if there is no :class:`roles.models.SecurityAccess`
            object related with the view (to minimize administrative tasks).
      c If there is an SecurityAccess object for the view:
        + TEST: The access to the view must be protected as object instruct.

    The tests to be done are:
    1 TEST if login is required for a view without related
      :class:`roles.models.SecurityAccess` object and belonging to a NOT
      PUBLIC application.
    2 TEST if the access configured for the view is correct against the
    information found in :class:`roles.models.SecurityAccess` object.

    Expected result
    ~~~~~~~~~~~~~~~

    * Fail: When between all possible site's url, there is one or more views
      that:
      a Or Fail TEST 1
      b Or Fail TEST 2
      c The view has escape all possibilities.



    Cosas a testear.
    Si una vista utiliza login_required el test del sitio debería advertirlo,
    si es posible, y verificar si está OK, es decir sólo se require estar
    logueado.

    """
    pass

# from unittest.case import TestCase
# import pytest
#
# from roles.utils import get_applications_view_names
# from roles.models import SecurityAccess
#
#
# class TestSiteSecurity(TestCase):
#     """
#     This test will check the security across the site (or Django project).
#
#     Some thing to take think about:
#     """
#
#     @pytest.mark.django_db
#     def test_site_security(self):
#         no_configured_views = []
#         from src.urls import urlpatterns
#         # print(urlpatterns)
#         for app_name, view_name in get_applications_view_names():
#             url_name = '{}:{}'.format(app_name, view_name)
#             configuration = SecurityAccess.objects.filter(url_name__iexact=url_name)
#             if configuration.count() == 0:
#                 no_configured_views.append(url_name)
#         if len(no_configured_views) > 0:
#             self.fail(u'The next Django\'s URLs: {} do not have a security configured'.format(
#                 no_configured_views))
#         self.assertTrue(True)


##############################################################################
################ Legacy code #################################################
#: TODO: Are this function realy needed?
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
# from importlib import import_module
# from django.urls import URLPattern, URLResolver
# from django.conf import settings
# import os
# from importlib import import_module
#
# from django.conf import settings
#
#
# URLCONF_FILES = ['../tests/urls.py']
#
#
# def get_installed_app():
#     """
#     Function to get actual installed applications in :setting:`INSTALLED_APP`.
#     All installed applications should have a declared *urls.py* and from here
#     django-roles will discover all active views: A view without url configured
#     is considered as inactive view because it should not be possible to access
#     that view.
#     :return:
#     """
#     return settings.INSTALLED_APPS
#
#
# def get_site_url_file():
#     return import_module(settings.ROOT_URLCONF).urlpatterns
#
#
# def get_url_files():
#     """
#     For each application will search all files named as defined in
#     URLCONF_FILES.
#
#     :return: Python list with tuples (aplication_name, url_file_path)
#     * aplication_name: Directory name where the url file were found.
#     * url_file_path: Full path to a founded url file
#     """
#     url_files = []
#     root_dir = os.path.dirname(os.path.dirname(os.path.dirname(
#                                                os.path.abspath(__file__))))
#     urlconf_files = URLCONF_FILES
#     for application_name in os.listdir(root_dir):
#         # Cicle through root directory elements
#         if not os.path.isfile(os.path.join(root_dir, application_name)):
#             # Ignore files
#             if application_name in settings.INSTALLED_APPS:
#                 # Exclude directory that are not applications
#                 for file_ in urlconf_files:
#                     # Cicle through declared URLConf files
#                     url_file_path = os.path.join(root_dir, application_name, file_)
#                     if os.path.isfile(url_file_path):
#                         url_files.append((application_name, url_file_path))
#     return url_files
#
#
# def get_applications_view_names():
#     """
#     For each application
#
#
#     :return: Python list of tuples (application_name, view_name)
#     """
#     result = []
#     for app_name, url_file in get_url_files():
#         file_ = open(url_file, 'r')
#         for line in file_:
#             app_name_defined = line.split("app_name")
#             if len(app_name_defined) > 1:
#                 app_name_defined = app_name_defined[1].split("=")
#                 if len(app_name_defined) > 1:
#                     app_name = app_name_defined[1].strip('\', \n, \"')
#             # Cicle through urls.py files
#             splited_line = line.split(" name=")
#             if len(splited_line) > 1:
#                 view_name = splited_line[1].split(")")
#                 if len(view_name) > 1:
#                     result.append((app_name, view_name[0].replace('\'', '').replace('\"', '')))
#     return result
#
#
# def get_view_names_choices():
#     """
#
#     :param application:
#     :return:
#     """
#     result = []
#     for app_name, view_name in get_applications_view_names():
#         result.append(('{}:{}'.format(app_name, view_name), '{}:{}'.format(app_name, view_name)))
#     return result
#
#
# def get_site_views():
#     """
#     This function
#
#     1 Get *main urlpatterns* for the site. This is starting point to get all
#       possible views that can be accessed by a user under the conception that
#       if there is no URL pointing the view, there is no way to access a view.
#     2 *main urlpatterns* can be a list of URLResolver and/or URLPattern
#       objects.
#     3 An URLResolver can be a list of URLResolver and/or URLPattern objects.
#
#     URLResolver provides:
#     a app_name
#     b namespace
#
#     URLPattern provides:
#     a name
#     b lookup_str
#     c pattern
#
#     Debe haber una función que reciba un URLResolver y recorra su contenido,
#     1 si un elemento es un URLResolver se vuelve a llamar a si misma (recursivo)
#       con el URLResolver
#     2 Si el elemento es un URLPattern, se obtienen los datos, se concatena el
#       nombre de la aplicación y se suma a la lista que se va devolviendo.
#
#     :return: A tuple: (path, name, view):
#     * *path*: The path to be verified: /polls/<...>/result
#     * *name*: Name of the view: polls:result
#     * *view*: Class o function called when path is hit.
#     """
#     # Main urlpatterns for the site:
#     url_patterns = import_module(settings.ROOT_URLCONF).urlpatterns
#     for url in url_patterns:
#         if isinstance(url, URLPattern):
#             print(url)
#         else:
#             print(url.url_patterns)
#     return []
#
#
# def get_site_urls(url_patterns):
#     result = []
#     for url in url_patterns:
#         if isinstance(url, URLResolver):
#             result.extend({url.app_name: get_site_urls(url.url_patterns)})
#         elif isinstance(url, URLPattern):
#             result.append(url)
#     return result
#
#
# def get_url_app_view():
#     result = []
#     url_patterns = import_module(settings.ROOT_URLCONF).urlpatterns
#     urls = list(set(get_site_urls(url_patterns)))
#     for url in urls:
#         if isinstance(url, dict):
#             for key_, values in url:
#                 for value in values:
#                     result.append(('{}:{}'.format(key_, value),
#                                   value.lookup_str, value.pattern))
#         else:
#             print(url)
#             # result.append((url.name, url.lookup_str, url.pattern))
#     return result


##############################################################################
################ End Legacy code #############################################

