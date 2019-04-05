# encoding='utf-8'
# Translation https://stackoverflow.com/questions/2938692/
# django-internationalization-for-admin-pages-translate-model-name-and-attribute

from django.db import models
try:
    from django.utils.translation import ugettex_lazy as _
except:
    from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group


class ViewAccess(models.Model):
    """
    Implements security in views having a name.

    The view name is *view* attribute value. The security for view name is
    configured with next two attributes: type (type of security) and roles
    (only if type is By role).
    """

    PUBLIC = 'pu'
    AUTHORIZED = 'au'
    BY_ROLE = 'br'

    ACCESS_TYPES = (
        (PUBLIC, _('Public')),
        (AUTHORIZED, _('Authorized')),
        (BY_ROLE, _('By role'))
    )

    #: View's name to be secured. Value can be just a view name 'objects_a',
    #: with application name: 'app_name:index', or a nested configurations with
    #: namespaces: 'namespace_1:namespace_2:index'.
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
    #: This attributes can always be empty. If the type selected is *By role*
    #: and no roles are added to this attribute, then *checkviewaccess* will
    #: report an ERROR.
    roles = models.ManyToManyField(Group, help_text=
                                   _(u'Select the groups (roles) with view '
                                     u'access if access type = By role.'),
                                   related_name='view_access',
                                   verbose_name=_(u'Roles'),
                                   blank=True)

    class Meta:
        verbose_name = _('View access')
        verbose_name_plural = _('Views access')

    def __str__(self):
        return self.view


class TemplateAccess(models.Model):
    """
    Implements content security.

    This model let administrator to add or remove Groups (roles) from *roles*
    attribute. In templates, users belonging to any added group will pass the
    check.
    """
    #: Template's flag, text label, to identify each template access object.
    #: Flag must be unique.
    flag = models.CharField(max_length=255, unique=True, default=None,
                            help_text=_(u'Unique between all applications.'
                                        u'Flag is used with template tag '
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
