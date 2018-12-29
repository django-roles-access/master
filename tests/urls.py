from django.conf.urls import url
try:
    from django.urls import include
except:
    from django.conf.urls import include

from . import views


urlpatterns = [
    url(r'^direct_access_view/$', views.protected_view_by_role,
        name='direct_access_view'),
    url(r'^role-included[135]/',
        include('tests.include_roles_url')),
    url(r'^role-included2/',
        include('tests.include_roles_url', namespace='app-ns2')),
    url(r'^nest1/', include('tests.include_nested_namespaces',
                            namespace='nest1_namespace')),
]
