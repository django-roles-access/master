from functools import wraps

from django_roles_access.tools import check_access_by_role, get_no_access_response


def access_by_role(view):
    """
    Check if logged user can access the decorated function or method.
    """
    @wraps(view)
    def _view(request, *args, **kwargs):
        if check_access_by_role(request):
            return view(request, *args, **kwargs)
        return get_no_access_response()

    _view.access_by_role = True
    return _view
