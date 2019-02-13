================================
Levels of access to applications
================================

Mainly django-roles is about setting roles access to views. This is done in
Admin creating an :class:`ViewAccess` object for each view. There are 3
possible type of access to be set:

* Public: Any user can access the view.

* Authorized: Only authorized :class:`django.contrib.auth.User` can access
  the view. Is equivalent to
  :func:`django.contrib.auth.decorators.login_required`.

* By roles: Only :class:`django.contrib.auth.User` belonging to
  :class:`django.contrib.auth.Group` that has been granted access to the
  view can access the view.


=====================
Without configuration
=====================
If an application is not declared as any of the others, but there is an
:class:`roles.models.ViewAccess` object associated to a view belonging to that
application and the view is protected with decorator or middleware is being
used ViewAccess object will be used to restrict the access.


.. _`Namespace and View Name`:

========================
Namespaces and View Name
========================

When creating a :class:`roles.models.ViewAccess` object, the value of **view**
attribute can be:

* `view_name`
* `app_name:view_name`
* `namespace:view_name`
* `nest_namespace:namespace:view_name`


#TODO: Check how official doc talk about this and link.
URLConf configuration (*urls.py*) gives the possible values. As also
URLConf configuration is used by Django to serve Site's URL.

???The value of *ROOT_URLCONF* is used to know all possible views.???



=========
Arguments
=========

Django-roles do not take view's arguments into consideration. This is true
except for request argument (key in Django-roles works).

As Django's URL dispatcher found a match (with or without regex to solve) the
view is called. When the view is called is when Django-roles start to grant
access, or not. And this is done with view name and application name (or
namespaces), only request argument is needed.

This is important if your site have a middleware that change the request.


============
Template Tag
============

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



==============================
Views without application name
==============================

When a views have no application associated, they will be classified in a
group under application name equal to constant
*django_roles.utils.APP_NAME_FOR_NONE*
