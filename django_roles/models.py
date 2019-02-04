# encoding='utf-8'
# Translation https://stackoverflow.com/questions/2938692/
# django-internationalization-for-admin-pages-translate-model-name-and-attribute

from django.db import models
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import Group


class ViewAccess(models.Model):
    """
    Implements security by checking url_name of each declared view with the groups
    assigned to that view.
    """

    PUBLIC = 'pu'
    AUTHORIZED = 'au'
    BY_ROLE = 'br'

    ACCESS_TYPES = (
        (PUBLIC, _('Public')),
        (AUTHORIZED, _('Authorized')),
        (BY_ROLE, _('By role'))
    )

    #: View's name to be secured. Is possible to use namespace as part of the
    #: view's name.
    view = models.CharField(max_length=255, unique=True, default=None,
                            help_text=_(u'View name to be secured: '
                                        u'<em>namespace:view_name</em>'),
                            verbose_name=_(u'View'))
    #: The type of access as defined by ACCESS_TYPES
    type = models.CharField(max_length=2, choices=ACCESS_TYPES, default=None,
                            help_text=_(u'Type of access for the view. '
                                        u'Select from available options.'),
                            verbose_name=_(u'Type'))
    #: One or more roles (:func:`django.contrib.auth.models.Group`) with access.
    roles = models.ManyToManyField(Group, help_text=
                                   _(u'Select the groups (roles) with view '
                                     u'access if access type = By role.'),
                                   related_name='view_access',
                                   verbose_name=_(u'Roles'))

    class Meta:
        verbose_name = _('View access')
        verbose_name_plural = _('Views access')

    def __str__(self):
        return self.view


class TemplateAccess(models.Model):
    """
    Implements security at template level.

    This model let administrator to add or remove Groups (roles) from *roles*
    attribute. In templates, users belonging to any added group will pass the
    check.
    """
    #: Template's flag for restriction by role.
    flag = models.CharField(max_length=255, unique=True, default=None,
                            help_text=_(u'Flag is used with template tag '
                                        u'check_role to restrict access in '
                                        u'templates.'),
                            verbose_name=_(u'Flag'))
    #: One or more roles (:func:`django.contrib.auth.models.Group`) with access.
    roles = models.ManyToManyField(Group, help_text=
                                   _(u'Select the groups (roles) with access '
                                     u'with check_role template tag and '
                                     u'flag.'),
                                   related_name='template_access',
                                   verbose_name=_(u'Roles'))

    class Meta:
        verbose_name = _('Template access')
        verbose_name_plural = _('Templates access')

    def __str__(self):
        return self.flag
