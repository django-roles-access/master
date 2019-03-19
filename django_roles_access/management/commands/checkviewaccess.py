# -*- coding: utf-8 -*-
"""
This test module will search for all site's urls and analyze their security
status.
"""
from importlib import import_module
from django.core.management.base import BaseCommand
try:
    from django.utils.translation import gettext as _
except:
    from django.utils.translation import ugettext as _
from django.conf import settings

from django_roles_access.tools import get_app_type
from django_roles_access.utils import (walk_site_url, get_views_by_app,
                                       view_access_analyzer, print_view_analysis)


DJANGO_ROLE_MIDDLEWARE = 'django_roles_access.middleware.RolesMiddleware'


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

        # 3. Analysis is done by application
        for app_name, views_list in views_by_app.items():
            self.stdout.write(
                self.style.SUCCESS(
                    _(u'\tAnalyzing {}:').format(app_name)))
            # Get application classification.
            app_type = get_app_type(app_name)
            if app_type:
                self.stdout.write(
                    self.style.SUCCESS(
                        _(u'\t\t{} is {} type.').format(app_name, app_type)))
            else:
                self.stdout.write(
                    self.style.WARNING(
                        _(u'\t\t{} has no type.').format(app_name)))

            # if application does not have views list:
            if len(views_list) == 0:
                self.stdout.write(
                    self.style.WARNING(
                        _(u'\t\t{} does not have configured views.'.format(
                            app_name))))

            # 4. For each view of the analyzed application
            for url, callback, view_name in views_list:
                self.stdout.write(
                    self.style.SUCCESS(
                        _(u'\n\t\tAnalysis for view: {}'
                          u'\n\t\tView url: {}'.format(view_name, url))))

                analysis = view_access_analyzer(app_type, callback, view_name,
                                                site_active)

                print_view_analysis(self.stdout, self.style, analysis)

            # 5. End for app_name in views_by_app:
            self.stdout.write(
                self.style.SUCCESS(
                    _(u'\tFinish analyzing {}.').format(app_name)))

        # 6. End of report
        self.stdout.write(self.style.SUCCESS(
            _(u'End checking view access.')))
