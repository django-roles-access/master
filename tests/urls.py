from django.conf.urls import url
from django.urls import include

from . import views

urlpatterns = [
    url(r'^role-included[135]/',
        include('roles.tests.include_roles_url', namespace='role-ns1')),
    url(r'^role-included2/',
        include('roles.tests.include_roles_url', namespace='app-ns2')),
    url(r'^direct_access_view/$', views.protected_view_by_role,
        name='direct_access_view'),
]
