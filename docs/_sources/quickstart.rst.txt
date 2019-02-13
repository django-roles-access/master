============
Introduction
============

``django_roles`` is a Django app for securing access to views. It's built on top
of :class:`django.contrib.auth.models.Group` that will be interpreted as role
. This app do not interfere with the work of any ``django.contrib.auth
.decorators`` used in the project.

Main features:

* Once configured, all administration for securing access to views is done in
  admin site at run time.

* Not extra code required:

  * In case of being using ``django_roles`` decorator or mixin, all what is
    needed is to decorate the view function or prepend the mixin in class based
    view definition.

  * When using ``django_roles`` middleware no more code is required.

* Access to views can be controlled with two element:

  1. View access object: An object with two attribute: view name and roles.

  2. Application classifications in project settings.

* ``django_roles`` register an action called ``checkviewaccess`` that will
  report project views access security no matter if ``django_roles`` tools are
  used or not. To use it just:

::

    python manage.py checkviewaccess

.. note::

    The installation and use of *Django roles* will not have any effect in views
    with already restricted access. For example, a view restricted with
    decorator :func:`django.contrib.auth.decorators.login_required`
    will remain having the restriction plus the new restrictions added by
    Django roles


============
Requirements
============

Django roles use :class:`django.contrib.auth.models.Group`,
:class:`django.contrib.auth.models.User` and *view names* to control access
to views. Also *Django admin interface* in necessary to create and administrate
*view control access* (:class:`django_roles.models.ViewAccess`).

So Django roles is dependent of *Django admin site* and because of this it has
the same requirements than *Django admin site*. This can be checked in the
official documentation: `Django admin site`_.

.. _`Django admin site`: https://docs.djangoproject.com/en/dev/ref/contrib/admin/

.. _QuickStart:

===========
Quick start
===========

------------------------------
Installation and configuration
------------------------------

1. Install "django-roles" from pypi:

::

   pip install django-roles

2. Add *"django_roles"* to your INSTALLED_APPS setting:

::

   INSTALLED_APPS = [
       ...
       'django_roles',
   ]


3. Run migrations to create the ``django_roles`` models:
::

    python manage.py migrate

.. note::

   Once Django roles is installed, by default all Django sites views keeps their
   **access status**. If they were public, they will remain
   being public. If they were restricted by some logic (like
   :func:`django.contrib.auth.decorators.login_required`), they will keep
   restricted by the same logic.

--------------------
Access configuration
--------------------

Quick access configuration in two steps.

Step 1
======

In *Django admin* interface to create an
:class:`django_roles.models.ViewAccess` object and configure it:

1. In **view** select the view you want to secure. More about this in
   :ref:`Namespace and View Name`.

2. In **type** select the *access type* for the view:

   * **Public**: Any visitor can access the view.

   * **Authorized**: Only authorized (logged)
     :class:`django.contrib.auth.models.User` can access the view.

   * **By roles**: Only :class:`django.contrib.auth.models.User` belonging to
     any :class:`django.contrib.auth.models.Group` added to *roles* attribute
     will access the view.

3. If *By role* access type was selected, add to **roles** attribute the
   :class:`django.contrib.auth.models.Group` whose members will have access
   to the view.

Step 2
======

The second step is about using :func:`django_roles.decorators.access_by_role`
decorator to decorate the view you want to secure.
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

