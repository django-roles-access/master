from django.utils.decorators import method_decorator

from django_roles_access.decorator import access_by_role


class RolesMixin(object):
    """
    A mixin that user access_by_role decorator for dispatch method.
    """

    @method_decorator(access_by_role)
    def dispatch(self, request, *args, **kwargs):
        return super(RolesMixin, self).dispatch(request, *args, **kwargs)
