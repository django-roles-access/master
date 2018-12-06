from django.conf.urls import url
try:
    from django.urls import include
except:
    from django.conf.urls import include

from . import views


nest_test_2 = [
    url(r'^direct_access_view/$', views.protected_view_by_role,
        name='direct_access_view'),
]

nest_test_1 = [
    url(r'^nest2/$', include(nest_test_2, namespace='nest_test_2')),
    url(r'^view_by_role/$', views.protected_view_by_role,
        name='view_protected_by_role'),
]

urlpatterns = [
    url(r'^role-included[135]/',
        include('tests.include_roles_url', namespace='role-ns1')),
    url(r'^role-included2/',
        include('tests.include_roles_url', namespace='app-ns2')),
    url(r'^direct_access_view/$', views.protected_view_by_role,
        name='direct_access_view'),
    url(r'^nest1/$', include(nest_test_1, 'nest1')),
]
