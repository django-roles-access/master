from django.conf.urls import url
try:
    from django.urls import include
except:
    from django.conf.urls import include

app_name = 'roles-nested-namespace'

urlpatterns = [
    url(r'^nest2/', include('tests.include_roles_namespace',
                            namespace='nest2_namespace')),
]