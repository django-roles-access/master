"""
This test module will search for all site's urls and analyze their security
status.
"""
from unittest.case import TestCase
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Manage command apptask'

    def add_arguments(self, parser):
        """
        The command can receive arguments. They have to be
        declared in add_arguments method.
        """
        parser.add_argument('ids', nargs='+', type=int)

    def handle(self, *args, **options):
        """
        This method implements the manage.py command
        """
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







#: TODO Recover applications from settings or database or user must define it?
# from unittest.case import TestCase
# import pytest
#
# from roles.utils import get_applications_view_names
# from roles.models import SecurityAccess
#
#
# # TODO: Si la vista está entre las no configuradas, fallara si no solicita login. En caso de no estar
# # TODO: declarada, debería permitir el acceso de todos si han iniciado sesion
# # TODO: Se deberia poder declarar aplicaciones publicas de modo que pueda acceder a ellas sin haber
# # TODO: iniciado sesion
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
