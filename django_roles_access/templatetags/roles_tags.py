from django import template
from django_roles_access.models import TemplateAccess

register = template.Library()


@register.filter(name='check_role')
def check_role(user, flag):
    """
    **flag** is a unique string used to restrict access by role in template
    content. With **flag** is recover an :class:`roles.models.TemplateAccess`
    object.

    :param flag: :attribute:`roles.models.TemplateAccess.flag`.
    :param user:
    :return:
    """
    try:
        if user.is_superuser:
            return True
        template_flag = TemplateAccess.objects.get(flag__exact=flag)
        for group in user.groups.all():
            if group in template_flag.roles.all():
                return True
        return False
    except:
        return False
