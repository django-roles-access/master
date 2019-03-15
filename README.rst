============
Django Roles
============

Application for securing Django site view access by roles
(:class:`django.contrib.auth.models.Group`).

``django_roles`` is a Django app for securing access to views. It's built on top
of :class:`django.contrib.auth.models.Group` interpreted as role.
The objective of the app are:

* Provide secure access to views.

* Be able to administrate access to views without the need to restart the
  server (at run time).

* Minimize the need of new code, or eliminate it at all (when using
  ``django_roles`` middleware). Also free developers from view access task/code.

* ``django_roles`` also provides a security report by registering
  ``checkviewaccess`` action.

Works with:
* Django 1.10+ (Python 2.7, Python 3.5+)
* Django 2 (Python 3.5+)


============
Requirements
============

Django roles use :class:`django.contrib.auth.models.Group`,
:class:`django.contrib.auth.models.User`. Also *Django admin interface* is
necessary to create and administrate *views access*
(:class:`django_roles.models.ViewAccess`).
So Django roles is dependent of *Django admin site* and because of this it has
the same requirements than it. This can be checked in the
official documentation: `Django admin site`_.

.. _`Django admin site`: https://docs.djangoproject.com/en/dev/ref/contrib/admin/

Last requirement is to give names in *urls.py* files to views and
applications. Read more about this in :ref:`Required views and app name`.

.. _QuickStart:

===========
Quick start
===========

------------------------------
Installation and configuration
------------------------------

1. Install ``django_roles`` from pypi:

::

   pip install django-roles

2. Add *'django_roles'* to your INSTALLED_APPS setting:

::

   INSTALLED_APPS = [
       ...
       'django_roles',
   ]


3. Run migrations to create the ``django_roles`` models:
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

In *Django admin* interface create a
:class:`django_roles.models.ViewAccess` object and configure it:

1. **view** attribute: type the name of the view you want to secure. More about
   this in :ref:`Namespace and View Name`.

2. **type** attribute: select the *access type* for the view:

   * **Public**: Any visitor can access the view.

   * **Authorized**: Only authorized (logged)
     :class:`django.contrib.auth.models.User` can access the view.

   * **By roles**: Only :class:`django.contrib.auth.models.User` belonging to
     any added :class:`django.contrib.auth.models.Group` will access the view.

3. **roles** attribute: When *By roles* is selected as *access type*, this
   attribute hold any :class:`django.contrib.auth.models.Group`
   whose members will access the view.


Step 2
======

Use :func:`django_roles.decorators.access_by_role` decorator or
:class:`django_roles.mixin.RolesMixin` mixin in the view to be secured.

For example:

In case the view is a function:
::

    from django_roles.decorators import access_by_role

    @access_by_role()
    myview(request):
       ...


In case of classes based views use mixin:
::

    from django_roles.mixin import RolesMixin

    class MyView(RolesMixin, View):

        ...

.. note::

   When user has no access to a view, by default ``django_roles`` response with
   :class:`django.http.HttpResponseForbidden`.

.. note::

   Pre existent security behavior can be modified if a ``django_role``
   configuration for the same view results in forbidden access.
