# -*- coding: utf-8 -*-
"""
This test module will search for all site's urls and analyze their security
status.
"""
from importlib import import_module
from django.core.management.base import BaseCommand
from django.utils import timezone
try:
    from django.utils.translation import gettext as _
except:
    from django.utils.translation import ugettext as _
from django.conf import settings

from django_roles_access.tools import get_app_type
from django_roles_access.utils import (walk_site_url, get_views_by_app,
                                       view_access_analyzer, print_view_analysis)


DJANGO_ROLE_ACCESS_MIDDLEWARE = 'django_roles_access.middleware.RolesMiddleware'


class Command(BaseCommand):
    """
    **checkviewaccess** management command to analyze *site's views access*.
    """
    help = 'Manage command checkviewaccess'

    def add_arguments(self, parser):
        # Add optional argument issue # 2
        parser.add_argument(
            '--output-format',
            dest='format',
            type=str)

    def handle(self, *args, **options):
        """
        This method implements checkviewaccess command behavior.
        """
        self.with_format = False
        if options['format']:
            self.with_format = True

        if self.with_format:
            self.stdout.write(self.style.SUCCESS(
                _(u'Reported: {}'.format(timezone.now()))))
        else:
            self.stdout.write(self.style.SUCCESS(
                _(u'Start checking views access.')))

            # 1. All views are collected and grouped by application
            self.stdout.write(self.style.SUCCESS(
                _(u'Start gathering information.')))

        url = import_module(settings.ROOT_URLCONF).urlpatterns
        views_by_app = get_views_by_app(walk_site_url(url))

        # 2. Check if Django roles middleware is active or not
        if DJANGO_ROLE_ACCESS_MIDDLEWARE in settings.MIDDLEWARE:
            site_active = True
        else:
            site_active = False

        self.stdout.write(
            self.style.SUCCESS(
                _(u'Django roles access middleware is active: '
                  u'{}.').format(site_active)))

        if self.with_format:
            self.stdout.write(self.style.SUCCESS(
                _(u'App Name,Type,View Name,Url,Status,Status description')))
        else:
            self.stdout.write(self.style.SUCCESS(
                _(u'Finish gathering information.')))

        # 3. Analysis is done by application
        row_app = ''
        for app_name, views_list in views_by_app.items():
            if self.with_format:
                row_app += app_name + ','
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        _(u'\tAnalyzing {}:').format(app_name)))
            # Get application classification.
            app_type = get_app_type(app_name)
            if app_type:
                if self.with_format:
                    row_app += app_type
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            _(u'\t\t{} is {} type.').format(app_name, app_type)))
            else:
                if self.with_format:
                    row_app += 'app has no type'
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            _(u'\t\t{} has no type.').format(app_name)))

            # if application does not have views list:
            if len(views_list) == 0:
                if self.with_format:
                    self.stdout.write(row_app + ',,,,')
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            _(u'\t\t{} does not have configured views.'.format(
                                app_name))))

            # 4. For each view of the analyzed application
            row_view = ''
            for url, callback, view_name in views_list:
                if self.with_format:
                    row_view += view_name + ',' + url + ','
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            _(u'\n\t\tAnalysis for view: {}'
                              u'\n\t\tView url: {}'.format(view_name, url))))

                analysis = view_access_analyzer(app_type, callback, view_name,
                                                site_active)

                if self.with_format:
                    if 'ERROR:' in analysis:
                        row_view += _(u'Error,{}'.format(
                            analysis.split('ERROR: ')[1]
                        ))
                    elif 'WARNING:' in analysis:
                        row_view += _(u'Warning,{}'.format(
                            analysis.split('WARNING: ')[1]
                        ))
                    else:
                        row_view += _(u'Normal,{}'.format(analysis))
                else:
                    print_view_analysis(self.stdout, self.style, analysis)

                # End cycle for each app view
                if self.with_format:
                    self.stdout.write(row_app + ',' + row_view)
                    row_view = ''
            row_app = ''
            # 5. End for app_name in views_by_app:
            if not self.with_format:
                self.stdout.write(
                    self.style.SUCCESS(
                        _(u'\tFinish analyzing {}.').format(app_name)))

        # 6. End of report
        if self.with_format:
            self.stdout.write('')
        else:
            self.stdout.write(self.style.SUCCESS(
                _(u'End checking view access.')))

