from django.conf.urls import url

with_path = False  # Testing for Django 1
try:
    from django.urls import include
    from django.urls import path, re_path
    with_path = True  # Testing for Django 2
except:
    from django.conf.urls import include

from . import views

if with_path:
    urlpatterns = [
        path('direct_access_view/', views.protected_view_by_role,
             name='direct_access_view'),
        path('direct_view/', views.direct_view, name='direct_view'),
        re_path(r'^role-included[135]/',
                include('tests.include_roles_url')),
        path('role-included2/',
             include('tests.include_roles_url', namespace='app-ns2')),
        path('nest1/', include('tests.include_nested_namespaces',
                               namespace='nest1_namespace')),
    ]
else:
    urlpatterns = [
        url(r'^direct_access_view/$', views.protected_view_by_role,
            name='direct_access_view'),
        url(r'^direct_view/$', views.direct_view,
            name='direct_view'),
        url(r'^role-included[135]/',
            include('tests.include_roles_url')),
        url(r'^role-included2/',
            include('tests.include_roles_url', namespace='app-ns2')),
        url(r'^nest1/', include('tests.include_nested_namespaces',
                                namespace='nest1_namespace')),
    ]
