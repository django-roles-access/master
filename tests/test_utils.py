#: TODO: UnitTest must be implemented using mock and checking called_once_with
from django.test import TestCase


# class TestUtils(TestCase):

    # def test_get_site_views(self):
    #     """
    #     (path, name, view)
    #     :return:
    #     """
    #     expected = [('', 'polls:index', 'polls.views.IndexView'),
    #                 ('<int:pk>/', 'polls:detail', 'views.DetailView'),
    #                 ('<int:pk>/results/', 'polls:results', 'views.ResultsView'),
    #                 ('<int:question_id>/vote/', 'polls:vote', 'views.vote'),
    #                 ]
    #     # self.assertIn(expected, get_site_views())
    #     self.assertTrue(True)

    # def test_get_installed_app(self):
    #     """
    #
    #     """
    #     installed_app = settings.INSTALLED_APPS
    #     self.assertEqual(installed_app, get_installed_app())
    #
    # def test_get_site_url_file(self):
    #     url_pattern = import_module(settings.ROOT_URLCONF).urlpatterns
    #     for url in url_pattern:
    #         print(url)
    #     self.assertEqual(url_pattern, get_site_url_file())
    #     self.fail(u'Debug')
    #
    # def test_get_all_app(self):
    #     url_pattern = import_module(settings.ROOT_URLCONF).urlpatterns
    #     apps = []
    #     for url in url_pattern:
    #         apps.append(url.app_name)
