===================
Django Roles Access
===================

Application for securing Django site view access by roles
(*Django contrib Groups*).

``django_roles_access`` is a Django app for securing access to views. It's
built on top of *Django contrib Groups* interpreted as role. The objective of
the app are:

* Provide secure access to views.

* Be able to administrate access to views without the need to restart the
  server (at run time).

* Minimize the need of new code, or eliminate it at all (when using
  ``django_roles_access`` middleware). Also free developers from view access
  task/code.

* ``django_roles_access`` also provides a security report by registering
  ``checkviewaccess`` action.

Works with:

* Django 1.10+ (Python 2.7, Python 3.5+)

* Django 2 (Python 3.5+)


============
Requirements
============

Django roles access use *Django contrib Groups*, *Django contrib User*. Also
*Django
admin interface* is necessary to create and administrate *views access*
(``django_roles_access.models.ViewAccess``).
So Django roles access is dependent of *Django admin site* and because of
this it has the same requirements than it. This can be checked in the
official documentation: `Django admin site`_.

.. _QuickStart:

===========
Quick start
===========

------------------------------
Installation and configuration
------------------------------

1. Install ``django_roles_access`` from pypi:

::

   pip install django-roles-access

2. Add *'django_roles_access'* to your INSTALLED_APPS setting:

::

   INSTALLED_APPS = [
       ...
       'django_roles_access',
   ]


3. Run migrations to create the ``django_roles_access`` models:
::

    python manage.py migrate

.. note::

   If nothing else is done, then Django site security keeps without
   modification.

--------------------
Access configuration
--------------------

Quick access configuration in two steps.

Step 1
======

In *Django admin* interface create a ``django_roles_access.models.ViewAccess``
object and configure it:

1. **view** attribute: type the name of the view you want to secure.

2. **type** attribute: select the *access type* for the view:

   * **Public**: Any visitor can access the view.

   * **Authorized**: Only authorized (logged) *Django contrib User* can access
    the view.

   * **By roles**: Only *Django contrib User* belonging to
     any added *Django contrib user* will access the view.

3. **roles** attribute: When *By roles* is selected as *access type*, this
   attribute hold any *Django contrib Group* whose members will access the view.


Step 2
======

Use ``django_roles_access.decorators.access_by_role`` decorator or
``django_roles_access.mixin.RolesMixin`` mixin in the view to be secured.

For example:

In case the view is a function:
::

    from django_roles_access.decorators import access_by_role

    @access_by_role()
    myview(request):
       ...


In case of classes based views use mixin:
::

    from django_roles_access.mixin import RolesMixin

    class MyView(RolesMixin, View):

        ...

.. note::

   When user has no access to a view, by default ``django_roles_access``
   response with ``django.http.HttpResponseForbidden`1.

.. note::

   Pre existent security behavior can be modified if a ``django_role_access``
   configuration for the same view results in forbidden access.
