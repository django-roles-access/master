# -*- coding: utf-8 -*-
"""
This test module will search for all site's urls and analyze their security
status.
"""
from importlib import import_module

from django.core.management import BaseCommand
from django.conf import settings

from django_roles_access.tools import get_app_type
from django_roles_access.utils import (walk_site_url, get_views_by_app,
                                       view_access_analyzer,
                                       OutputReport)


DJANGO_ROLE_ACCESS_MIDDLEWARE = 'django_roles_access.middleware.RolesMiddleware'


class Command(BaseCommand):
    """
    **checkviewaccess** management _output to analyze *site's views access*.
    """
    help = 'Manage _output checkviewaccess'

    def add_arguments(self, parser):
        # Add optional argument issue # 2
        parser.add_argument(
            '--output-format',
            dest='format',
            type=str)

    def handle(self, *args, **options):
        """
        This method implements checkviewaccess _output behavior.
        """
        output = OutputReport(self.stdout, self.style)
        self.with_format = False
        if options['format']:
            self.with_format = True
            output.set_format('csv')
        output.write_header()

        # 1. Get information. All views are collected and grouped by application
        url = import_module(settings.ROOT_URLCONF).urlpatterns
        views_by_app = get_views_by_app(walk_site_url(url))

        # 2. Check if Django roles middleware is active or not
        if DJANGO_ROLE_ACCESS_MIDDLEWARE in settings.MIDDLEWARE:
            site_active = True
        else:
            site_active = False
        output.write_middleware_status(site_active)

        output.write_end_of_head()
        # 3. Analysis is done by application
        for app_name, views_list in views_by_app.items():
            # Get application classification.
            app_type = get_app_type(app_name)
            output.process_application_data(app_name, app_type, views_list)

            # 4. For each view of the analyzed application
            for url, callback, view_name in views_list:
                output.process_view_data(view_name, url)

                analysis = view_access_analyzer(app_type, callback, view_name,
                                                site_active)
                output.write_view_access_analyzer(analysis)

            output.close_application_data(app_name)

        # 6. End of report
        output.write_footer()

