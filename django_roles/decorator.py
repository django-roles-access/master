from functools import wraps

from django_roles.tools import check_access_by_role, get_no_access_response


def access_by_role(view):
    """
    Check if logged user can access the decorated function or class.

    A user (:class:`django.contrib.auth.models.User`) can access the decorated
    function or class when it belong to a
    :class:`django.contrib.auth.models.Group` with access given by an object of
    type :class:`roles.models.ViewAccess`.

    PermissionDenied is raised if user has no access.
    """
    @wraps(view)
    def _view(request, *args, **kwargs):
        if check_access_by_role(request):
            return view(request, *args, **kwargs)
        return get_no_access_response()

    _view.access_by_role = True
    return _view
