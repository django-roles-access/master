from django.core.exceptions import PermissionDenied
from roles.tools import check_access_by_role
# TODO: Create a ViewMixin which will implement the decorator.


def access_by_role(func=None):
    """
    Check if logged user can access the decorated function or class.

    A user (:class:`django.contrib.auth.models.User`) can access the decorated
    function or class when it belong to a
    :class:`django.contrib.auth.models.Group` with access given by an object of
    type :class:`roles.models.ViewAccess`.

    PermissionDenied is raised if user has no access.
    """
    def check_access(view):
        def _view(request, *args, **kwargs):
            if check_access_by_role(request):
                return view(request, *args, **kwargs)
            raise PermissionDenied

        _view.__name__ = check_access.__name__
        _view.__dict__ = check_access.__dict__
        _view.__doc__ = check_access.__doc__
        _view.access_by_role = True
        return _view
    # Let use it: foo = access_by_role(foo)
    if func:
        return check_access(func)
    return check_access
