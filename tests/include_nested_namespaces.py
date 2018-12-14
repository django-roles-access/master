from django.conf.urls import url
try:
    from django.urls import include
except:
    from django.conf.urls import include

from . import views


app_name = 'roles-nested-namespace'

urlpatterns = [
    url(r'^nest3/', include('tests.include_roles_namespace',
                             namespace='nest3')),
]