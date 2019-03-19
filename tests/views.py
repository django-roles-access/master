"""
This views are used for testing.
"""
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View

from django_roles_access.decorator import access_by_role
from django_roles_access.mixin import RolesMixin


def direct_view(request):
    """
    A simple view for testing default behavior.
    """
    return HttpResponse('THis is a simple view')


@access_by_role
def protected_view_by_role(request):
    """
    A simple view for testing access_by_role decorator.
    """
    user = request.user
    return HttpResponse('THis is a view processed by django-roles '
                        'middleware. Username is {{ user.username }}')


class ProtectedView(View):

    def get(self, request, *args, **kwargs):
        user = request.user
        return HttpResponse('THis is a view processed by django-roles '
                            'middleware. Username is {{ user.username }}')

    @method_decorator(access_by_role)
    def dispatch(self, request, *args, **kwargs):
        return super(ProtectedView, self).dispatch(request, *args, **kwargs)


class ProtectedMixinView(RolesMixin, View):

    def get(self, request, *args, **kwargs):
        user = request.user
        return HttpResponse('THis is a view processed by django-roles '
                            'middleware. Username is {{ user.username }}')


def middleware_view(request):
    """
    A simple view for testing django-roles middleware.
    """
    user = request.user
    return HttpResponse('THis is a view processed by django-roles '
                        'middleware. Username is {{ user.username }}')


class MiddlewareView(View):

    def get(self, request, *args, **kwargs):
        user = request.user
        return HttpResponse('THis is a view processed by django-roles '
                            'middleware. Username is {{ user.username }}')
