from django.conf.urls import url
try:
    from django.urls import include
except:
    from django.conf.urls import include

from . import views


app_name = 'roles-namespace'

urlpatterns = [
    url(r'^view_by_role/$', views.protected_view_by_role,
        name='view_protected_by_role'),
    url(r'^view_by_role_class/$', views.ProtectedView.as_view(),
        name='class_view_protected_by_role'),
    url(r'^mixin_class_view/$', views.ProtectedMixinView.as_view(),
        name='mixin_class_view'),
    url(r'^middleware_view_func/$', views.middleware_view,
        name='middleware_view_func'),
    url(r'^middleware_view_class/$', views.MiddlewareView.as_view(),
        name='middleware_view_class'),
]
