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


# TODO: 1)
# TODO: Incorporate namespace capabilities
# TODO: 2)
# TODO: Admin view field should be autocomplete? of all existing view without
# TODO: configuration.
class ViewAccess(models.Model):
    """
    Implements security by checking url_name of each declared view with the groups
    assigned to that view.
    """
    #: Asumme view name is app:view_name
    #: TODO: Correct next
    #: The url_name of the View which security access is being declared. Each
    #: url_name should have only one record, that will be: only one
    #: declaration of access right. This is why *unique* is required.
    view = models.CharField(max_length=255, unique=True)
    #:
    #:
    type = models.CharField(max_length=2, choices=ACCESS_TYPES)
    #: TODO: Correct next
    #: Relation ManyToMany with :func:`django.contrib.auth.models.Group`. The
    #: relation is ManyToMany because a View can
    #: be accessed by more than :func:`django.contrib.auth.models.Group`.
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
