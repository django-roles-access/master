import os
from importlib import import_module

from django.conf import settings


URLCONF_FILES = ['urls.py']


def get_installed_app():
    """
    Function to get actual installed applications in :setting:`INSTALLED_APP`.
    All installed applications should have a declared *urls.py* and from here
    django-roles will discover all active views: A view without url configured
    is considered as inactive view because it should not be possible to access
    that view.
    :return:
    """
    return settings.INSTALLED_APPS


def get_site_url_file():
    return import_module(settings.ROOT_URLCONF).urlpatterns


def get_url_files():
    """
    For each application will search all files named as defined in
    URLCONF_FILES.

    :return: Python list with tuples (aplication_name, url_file_path)
    * aplication_name: Directory name where the url file were found.
    * url_file_path: Full path to a founded url file
    """
    url_files = []
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(
                                               os.path.abspath(__file__))))
    urlconf_files = URLCONF_FILES
    for application_name in os.listdir(root_dir):
        # Cicle through root directory elements
        if not os.path.isfile(os.path.join(root_dir, application_name)):
            # Ignore files
            if application_name in settings.INSTALLED_APPS:
                # Exclude directory that are not applications
                for file_ in urlconf_files:
                    # Cicle through declared URLConf files
                    url_file_path = os.path.join(root_dir, application_name, file_)
                    if os.path.isfile(url_file_path):
                        url_files.append((application_name, url_file_path))
    return url_files


def get_applications_view_names():
    """
    For each application


    :return: Python list of tuples (application_name, view_name)
    """
    result = []
    for app_name, url_file in get_url_files():
        file_ = open(url_file, 'r')
        for line in file_:
            app_name_defined = line.split("app_name")
            if len(app_name_defined) > 1:
                app_name_defined = app_name_defined[1].split("=")
                if len(app_name_defined) > 1:
                    app_name = app_name_defined[1].strip('\', \n, \"')
            # Cicle through urls.py files
            splited_line = line.split(" name=")
            if len(splited_line) > 1:
                view_name = splited_line[1].split(")")
                if len(view_name) > 1:
                    result.append((app_name, view_name[0].replace('\'', '').replace('\"', '')))
    return result


def get_view_names_choices():
    """

    :param application:
    :return:
    """
    result = []
    for app_name, view_name in get_applications_view_names():
        result.append(('{}:{}'.format(app_name, view_name), '{}:{}'.format(app_name, view_name)))
    return result
