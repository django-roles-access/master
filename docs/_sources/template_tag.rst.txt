=========================
Django roles template tag
=========================

Django roles *template tag* is a method to restrict access by role to content.

``django_roles`` decorator, mixin or middleware restrict access to a
view. In this way, restriction is applied to all content of the view. With
``django_roles`` *template tag* is possible to restrict access to portions of
content of a view.

As the name could suggest, *template tag* is used in Django templates. An
example of use could be to create dynamic menu, where some menu appears to user
or not depending in his role.

For using Django roles template tag:
::

    {% load roles_tags %}
    ...
    {% if request.user|check_role:'reports_menu' %}
        check_access
    {% endif %}


Is required to configure a DjangoTemplate backend in *settings* file. If not,
when trying to use it, an exception will be raised:
::

    django.core.exceptions.ImproperlyConfigured: No DjangoTemplates backend is
    configured.

