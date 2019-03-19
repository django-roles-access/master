from django_roles_access.tools import check_access_by_role, get_no_access_response


class RolesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not check_access_by_role(request):
            return get_no_access_response()

        response = self.get_response(request)

        # Only useful for unit test.
        response.django_roles = True

        return response
