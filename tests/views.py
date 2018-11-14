"""
This views are used for testing.
"""
from django.http import HttpResponse
from django.template import Template, Context
from django.utils.decorators import method_decorator
from django.views import View

from roles.decorators import access_by_role
from roles.mixin import RolesMixin


@access_by_role
def protected_view_by_role(request):
    """
    A simple view for testing access_by_role decorator
    """
    t = Template('This is an access_by_role protected test. Username is '
                 '{{ user.username }}.'
                 , name='Login Template')
    c = Context({'user': request.user})

    return HttpResponse(t.render(c))


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
    t = Template('This is a view processed by django-roles middleware. '
                 'Username is {{ user.username }}.'
                 , name='Login Template')
    c = Context({'user': request.user})

    return HttpResponse(t.render(c))


class MiddlewareView(View):

    def get(self, request, *args, **kwargs):
        user = request.user
        return HttpResponse('THis is a view processed by django-roles '
                            'middleware. Username is {{ user.username }}')
