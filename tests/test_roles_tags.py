from unittest import TestCase as UnitTestCase
from django.template import Template, Context
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


try:
    from unittest.mock import Mock, patch
except:
    from mock import Mock, patch

from django_roles_access.models import TemplateAccess
from django_roles_access.templatetags.roles_tags import check_role

User = get_user_model()


class UnitTestRolesTags(UnitTestCase):

    def test_roles_tags_show_content_for_superuser(self):
        user = Mock()
        user.is_superuser = True
        self.assertTrue(check_role(user=user, flag='fake-flag'))

    @patch('django_roles_access.templatetags.roles_tags.TemplateAccess.objects')
    def test_roles_tags_show_content_for_flag_and_user_in_roles(
            self, mock_ta_objects
    ):
        user = Mock()
        user.is_superuser = False
        user.groups.all.return_value = ['fake-group']
        template_flag = Mock()
        template_flag.roles.all.return_value = ['fake-group', 'other-group']
        mock_ta_objects.get.return_value = template_flag
        self.assertTrue(check_role(user=user, flag='fake-flag'))

    @patch('django_roles_access.templatetags.roles_tags.TemplateAccess.objects')
    def test_roles_tags_not_show_content_for_flag_and_user_not_in_roles(
            self, mock_ta_objects
    ):
        user = Mock()
        user.is_superuser = False
        user.groups.all.return_value = ['no-group']
        template_flag = Mock()
        template_flag.roles.all.return_value = ['fake-group', 'other-group']
        mock_ta_objects.get.return_value = template_flag
        self.assertFalse(check_role(user=user, flag='fake-flag'))


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
        template_acces.save()
        self.user.groups.add(self.group)
        self.user.save()
        rendered = self.TEMPLATE.render(Context({'request': self.request}))
        self.assertIn('checked access', rendered)

    def test_template_tag_show_content_if_superuser(self):
        template_acces, created = TemplateAccess.objects.get_or_create(
            flag='test-flag')
        template_acces.roles.add(self.group)
        template_acces.save()
        self.user.is_superuser = True
        rendered = self.TEMPLATE.render(Context({'request': self.request}))
        self.assertIn('checked access', rendered)

    def test_template_tag_do_not_show_content_if_no_template_access(self):
        rendered = self.TEMPLATE.render(Context({}))
        self.assertNotIn('checked access', rendered)

    def test_template_tag_do_not_show_content_if_user_not_in_roles(self):
        template_acces, created = TemplateAccess.objects.get_or_create(
            flag='test-flag')
        template_acces.roles.add(self.group)
        template_acces.save()
        self.user.groups.remove(self.group)
        self.user.save()
        rendered = self.TEMPLATE.render(Context({'request': self.request}))
        self.assertNotIn('checked access', rendered)
