from unittest import mock, TestCase as UnitTestCase
from django.template import Template, Context
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from django_roles.models import TemplateAccess
from django_roles.templatetags.roles_tags import check_role

User = get_user_model()


class UnitTestRolesTags(UnitTestCase):

    def test_roles_tags_show_content_for_superuser(self):
        user = mock.Mock()
        user.is_superuser = True
        assert check_role(user=user, flag='fake-flag')

    def test_roles_tags_show_content_for_existing_flag_and_user_in_roles(self):
        # Use model mocking.
        user = mock.Mock()
        user.is_superuser = True
        assert check_role(user=user, flag='fake-flag')


class IntegratedTestRolesTags(TestCase):

    TEMPLATE = Template("{% load roles_tags %} "
                        "{% if request.user|check_role:'test-flag' %} "
                        "checked access {% endif %} ")

    def setUp(self):
        self.user, created = User.objects.get_or_create(username='test')
        self.group, created = Group.objects.get_or_create(name='Test-group')
        self.request = RequestFactory()
        self.request.user = self.user

    def test_template_tag_show_content(self):
        template_acces, created = TemplateAccess.objects.get_or_create(
            flag='test-flag')
        template_acces.roles.add(self.group)
        self.user.groups.add(self.group)
        self.user.save()
        rendered = self.TEMPLATE.render(Context({'request': self.request}))
        self.assertIn('checked access', rendered)

    def test_template_tag_do_not_show_content_if_no_template_access(self):
        rendered = self.TEMPLATE.render(Context({}))
        self.assertNotIn('checked access', rendered)

    def test_template_tag_do_not_show_content_if_user_not_in_roles(self):
        template_acces, created = TemplateAccess.objects.get_or_create(
            flag='test-flag')
        template_acces.roles.add(self.group)
        self.user.groups.remove(self.group)
        self.user.save()
        rendered = self.TEMPLATE.render(Context({'request': self.request}))
        self.assertNotIn('checked access', rendered)
