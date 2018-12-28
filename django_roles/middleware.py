from django.core.exceptions import PermissionDenied

from django_roles.tools import check_access_by_role


class RolesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not check_access_by_role(request):
            raise PermissionDenied

        response = self.get_response(request)

        # Only useful for unit test.
        response.django_roles = True

        return response
