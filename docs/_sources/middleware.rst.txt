=============================
Using Django roles middleware
=============================

It is also possible to use Django roles as middleware. This could be useful in
cases where all (or many) applications views should have controlled access.

For example, a requirement could be to all user needing to be logged-in to
access any views of a particular application. Possible solutions to this
could be (between others):

* Use *login_required*. in all applications views.

* Use a hook at URLConf configuration.

* Or use *Django roles middleware*, an declare the application as *Authorized*.

.. note::

    To know more about application classification read:
    :ref:`Applications type`.


------------
Installation
------------

In Django's site *settings* file add *django_roles.middleware.RolesMiddleware*
to MIDDLEWARE variable:

::

    MIDDLEWARE = [
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django_roles.middleware.RolesMiddleware',
        ...
    ]


-------------
Configuration
-------------

The last step is to classify installed applications in security
groups in Django site's *settings* file.

With Django roles is possible to classify installed applications in three
groups. When an application is classified in any of this three groups, and the
middleware installed, all access to applications's views will have the
default security of the group used to classify the application.

To know more about applications classification with Django roles read:
:ref:`Applications type`.


.. _`Applications type`:

=================
Applications type
=================

To declare *applications type* (and with this, their default security), is
necessary to add any of the next three variables (Python lists) in *settings*
file:

* NOT_SECURED.

* PUBLIC

* SECURED

.. note::

  By default if none of this 3 variables are declared in *settings*, all
  applications will be assumed as public, and their views will have public
  access security. Views will preserve their previous security status: for
  example if a view was restricted by *login_required* it will remain
  restricted by the same logic.

-----------
NOT_SECURED
-----------
List of applications not under site security.

The concept of NOT_SECURED application is to put together all applications that
not provide any view (no URLConf defined for the application). There are no
views with the need to be secured.

.. warning::

    If an application classified as NOT_SECURED and have views, anyone will be
    able to access this views.

------
PUBLIC
------
List of applications mainly for public access.

In PUBLIC applications views without a :class:`django_roles.models.ViewAccess`
object associated with it will no require authentication (user to be logged in)
and will have no more security configured by *Django roles*.

-------
SECURED
-------
List of applications with secured view access by roles
(:class:`django.contrib.auth.Group`).

When application is classified as a SECURED application, and there are views
without any :class:`django_roles.models.ViewAccess` object configured, they
will require the user to be logged. In other words, by default, the views of a
SECURED application behaves as if their security were *Authorized*
