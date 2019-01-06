# encoding='utf-8'

from django.db import models
try:
    from django.utils.text import gettext_lazy as _
except:
    from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group


ACCESS_TYPES = (
    ('pu', _('Public')),
    ('au', _('Authorized')),
    ('br', _('By role'))
)


class ViewAccess(models.Model):
    """
    Implements security by checking url_name of each declared view with the groups
    assigned to that view.
    """
    #: View's name to be secured. Is possible to use namespace as part of the
    #: view's name.
    view = models.CharField(max_length=255, unique=True)
    #:
    #:
    type = models.CharField(max_length=2, choices=ACCESS_TYPES)
    #:
    #:
    roles = models.ManyToManyField(Group)

    def __str__(self):
        return self.view


#: TODO: Complete and create documentation
class TemplateAccess(models.Model):
    """

    """
    #: Template's flag for restriction by role.
    flag = models.CharField(max_length=255, unique=True)
    #: One or more roles (:func:`django.contrib.auth.models.Group`) with access.
    roles = models.ManyToManyField(Group)

    def __str__(self):
        return self.flag
