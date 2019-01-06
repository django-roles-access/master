============
Django Roles
============

Application for securing Django site view access by roles
(:class:`django.contrib.auth.models.Group`).

Works with:
* Django 1.11 (Python 2.7, Python 3.6)
* Django 2 (Python 3.6)

============
Django Roles
============

Django roles is an application for securing a Django site by controlling
access to views.

Permissions to access views are given to
:class:`django.contrib.auth.models.Group`, and they can be interpreted as roles.
Is also possible to change a view access security at run time.

Works with:
* Django 1.11 (Python 2.7, Python 3.6)
* Django 2 (Python 3.6)


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


3. Run `python manage.py migrate` to create the django roles models.

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
   :class:`django.contrib.auth.Group` who's members should have access
   to the view.

Step 2
======

The second step is about using :func:`django_roles.decorators.access_by_role`
decorator to decorate the view you want to secure.
For example:

In case the view is a function:::

    from django_roles.decorators import access_by_role

    @access_by_role()
    myview(request):
       ...


In case of classes based views use mixin:::

    from django_roles.mixin import RolesMixin

    class MyView(View, RolesMixin):

        ...
