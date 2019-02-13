# -*- coding: utf-8 -*-
"""
This test module will search for all site's urls and analyze their security
status.
"""
from importlib import import_module
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _
from django.conf import settings

from django_roles.tools import get_setting_dictionary
from django_roles.utils import walk_site_url, get_views_by_app

DJANGO_ROLE_MIDDLEWARE = 'django_roles.middleware.RolesMiddleware'


class Command(BaseCommand):
    """
    **checkviewaccess** management command analyze *all site's views access*.

    The list with *all site's views* is obtained from *urlpatterns* attribute of
    the URLConf module configured in settings.ROOT_URLCONF.Each view access from
    the list of *site's views* is subject of analyze.

    Conclusion of analyze is reported by application as Django Roles let
    classify installed applications.
    """
    help = 'Manage command checkviewaccess'

    # def add_arguments(self, parser):
    #     """
    #     The command can receive arguments. They have to be
    #     declared in add_arguments method.
    #     """
    #     parser.add_argument('ids', nargs='+', type=int)

    def handle(self, *args, **options):
        """
        This method implements checkviewaccess command behavior.
        """
        self.stdout.write(self.style.SUCCESS(
            _(u'Start checking views access.')))

        # 1. All views are collected and grouped by application
        self.stdout.write(self.style.SUCCESS(
            _(u'Start gathering information.')))
        url = import_module(settings.ROOT_URLCONF).urlpatterns
        views_by_app = get_views_by_app(walk_site_url(url))
        configured_apps = get_setting_dictionary()
        self.stdout.write(self.style.SUCCESS(
            _(u'Finish gathering information.')))

        # 2. Check if Django roles middleware is active or not
        if DJANGO_ROLE_MIDDLEWARE in settings.MIDDLEWARE:
            site_active = True
        else:
            site_active = False
        self.stdout.write(
            self.style.SUCCESS(
                _(u'Django roles active for site: {}.').format(site_active)))

        self.stdout.write(self.style.SUCCESS(
            _(u'End checking view access.')))


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

