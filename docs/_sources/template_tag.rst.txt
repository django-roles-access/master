=========================
Django roles template tag
=========================

``django_roles`` *template tag* is a method to restrict access by role to
content.

``django_roles`` decorator, mixin, or middleware, restrict access to a
view. In this way, restriction is applied to all content of the view. With
``django_roles`` *template tag* is possible to restrict access to content
portions of a view.

``django_roles`` *template tag* is used in Django templates.

Example for using Django roles template tag:
::

    {% load roles_tags %}
    ...
    {% if request.user|check_role:'reports_menu' %}
        restricted content
    {% endif %}

If exist :class:`django_roles.models.TemplateAccess` object with name
*reports_menu*; only users in added :class:`django.contrib.auth.models.Group`
will see **restricted content**.

.. note::

   ``django_roles`` *template_tag* require DjangoTemplate backend to be
   configured in *settings file*. If not, when trying to use it, an exception
   will be raised:
   ::

       django.core.exceptions.ImproperlyConfigured: No DjangoTemplates
       backend is configured.

