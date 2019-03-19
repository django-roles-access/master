from django.contrib.auth.models import Group
from django.db import IntegrityError
try:
    from django.utils.translation import gettext as _
except:
    from django.utils.translation import ugettext as _
from django.test import TestCase
from django_roles_access.models import ViewAccess, TemplateAccess


class TestViewAccessModel(TestCase):

    def test_string_representation(self):
        view_access = ViewAccess(view="namespace:view-name", type='pu')
        view_access.save()
        self.assertEqual(str(view_access), "namespace:view-name")

    def test_view_help_text(self):
        expected_help_text = _(u'View name to be secured: '
                               u'<em>namespace:view_name</em>')
        actual_help_text = ViewAccess._meta.get_field('view').help_text
        self.assertEqual(expected_help_text, actual_help_text)

    def test_type_help_text(self):
        expected_help_text = _(u'Type of access for the view. '
                               u'Select from available options.')
        actual_help_text = ViewAccess._meta.get_field('type').help_text
        self.assertEqual(expected_help_text, actual_help_text)

    def test_roles_help_text(self):
        expected_help_text = _(u'Select the groups (roles) with view '
                               u'access if access type = By role.')
        actual_help_text = ViewAccess._meta.get_field('roles').help_text
        self.assertEqual(expected_help_text, actual_help_text)

    def test_roles_related_name(self):
        view_access = ViewAccess.objects.create(view="namespace:view-name",
                                                type='pu')
        view_access2 = ViewAccess.objects.create(view="namespace:other-view",
                                                 type='au')
        group, created = Group.objects.get_or_create(name='test')
        view_access.roles.add(group)
        view_access.save()
        view_access2.roles.add(group)
        view_access2.save()

        roles_access = group.view_access.all()

        self.assertIn(view_access, roles_access)
        self.assertIn(view_access2, roles_access)

    def test_view_attribute_is_required(self):
        view_access = ViewAccess(type='pu')
        with self.assertRaises(IntegrityError):
            view_access.save()
            view_access.full_clean()

    def test_view_attribute_is_unique(self):
        view_access = ViewAccess(view='app_name:same_name',
                                 type='pu')
        view_access.save()
        view_access2 = ViewAccess(view='app_name:same_name',
                                  type='au')
        with self.assertRaises(IntegrityError):
            view_access2.save()
            view_access2.full_clean()

    def test_type_attribute_is_required(self):
        view_access = ViewAccess(view='app_name:view_name')
        with self.assertRaises(IntegrityError):
            view_access.save()
            view_access.full_clean()

    def test_verbose_name_singular(self):
        self.assertEqual(str(ViewAccess._meta.verbose_name),
                         'View access')

    def test_verbose_name_plural(self):
        self.assertEqual(str(ViewAccess._meta.verbose_name_plural),
                         'Views access')


class TestTemplateAccessModel(TestCase):
    """
    Test model behavior requirement: flag attribute is required and unique.
    """
    def test_string_representation(self):
        template_access = TemplateAccess(flag="a-flag")
        template_access.save()
        self.assertEqual(str(template_access), "a-flag")

    def test_flag_help_text(self):
        expected_help_text = _(u'Unique between all applications.'
                               u'Flag is used with template tag '
                               u'check_role to restrict access in templates.')
        actual_help_text = TemplateAccess._meta.get_field('flag').help_text
        self.assertEqual(expected_help_text, actual_help_text)

    def test_roles_related_name(self):
        template_access = TemplateAccess.objects.create(flag="flag-1")
        template_access2 = TemplateAccess.objects.create(flag='flag-2')
        group, created = Group.objects.get_or_create(name='test')
        template_access.roles.add(group)
        template_access.save()
        template_access2.roles.add(group)
        template_access2.save()

        roles_template_access = group.template_access.all()

        self.assertIn(template_access, roles_template_access)
        self.assertIn(template_access2, roles_template_access)

    def test_roles_help_text(self):
        expected_help_text = _(u'Select the groups (roles) with access '
                               u'with check_role template tag and flag.')
        actual_help_text = TemplateAccess._meta.get_field('roles').help_text
        self.assertEqual(expected_help_text, actual_help_text)

    def test_flag_attribute_is_required(self):
        template_access = TemplateAccess()
        with self.assertRaises(IntegrityError):
            template_access.save()

    def test_flag_attribute_must_be_unique(self):
        template_access = TemplateAccess(flag='fake-flag')
        template_access.save()
        template_access_2 = TemplateAccess(flag='fake-flag')
        with self.assertRaises(IntegrityError):
            template_access_2.save()

    def test_verbose_name_singular(self):
        self.assertEqual(str(TemplateAccess._meta.verbose_name),
                         'Template access')

    def test_verbose_name_plural(self):
        self.assertEqual(str(TemplateAccess._meta.verbose_name_plural),
                         'Templates access')
