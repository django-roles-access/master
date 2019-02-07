from django.conf.urls import url
with_path = False  # Testing for Django 1
try:
    from django.urls import include
    from django.urls import path, re_path
    with_path = True  # Testing for Django 2
except:
    from django.conf.urls import include


app_name = 'roles-nested-namespace'

if with_path:
    urlpatterns = [
        path('nest2/', include('tests.include_roles_namespace',
                               namespace='nest2_namespace')),
    ]
else:
    urlpatterns = [
        url(r'^nest2/', include('tests.include_roles_namespace',
                                namespace='nest2_namespace')),
    ]
