.. _`Using Django roles middleware`:

=============================
Using Django roles middleware
=============================

In :ref:`Quick start` was explained how to configure in two steps a security
access for the view; but this require *new code*, to add a decorator or a
mixin is new code.

It is also possible to use Django roles as middleware, for example under next
two reasons:

* No new code wants to be added to project.

* Project size demand a solution for many applications, including third-party
  solutions

For example, a requirement could be to all user needing to be logged-in to
access any view of a particular application. Possible solutions to this
could be (between others):

* Use *login_required*. in all applications views.

* Use a hook at URLConf configuration.

* Or use *Django roles middleware*, an declare the application as *Authorized*.

.. note::

   To know more about application classification read after installation and
   configuration: :ref:`Applications type`.

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


.. warning::

   Once middleware is installed, to change the behavior of a view belonging
   to a particular application, at least a
   :class:`django_roles.models.ViewAccess` object needs to be created. If
   not, there will be no change while no application type is set
   (:ref:`Applications type`).


-------------
Configuration
-------------

The last step is to classify installed applications in security
groups in Django site's *settings* file.

With Django roles is possible to classify installed applications in three
types. When application is classified in any of this three types, and the
middleware installed, all access to applications's views will have the
default security of the type used to classify the application.

To know more about applications classification with Django roles read next:
:ref:`Applications type`.


.. _`Applications type`:

=================
Applications type
=================

To setup *applications type* (and with this, their default security), is
necessary to add any of the next three variables (Python lists) in
*settings file*:

* NOT_SECURED

* PUBLIC

* SECURED

.. note::

  By default if none of this 3 variables are declared in *settings*, all
  applications will be assumed as public, and their views will have public
  access security. Views will preserve their previous security status: for
  example, if a view was restricted by *login_required* it will remain
  restricted by the same logic.

-----------
NOT_SECURED
-----------
List of applications not under site security.

The concept of NOT_SECURED application is to put together all applications
not providing any view (no URLConf defined for the application). There are no
views with the need to be secured.

.. warning::

    If an application is classified as NOT_SECURED, and has views, anyone
    will be able to access this views.

.. warning::

    If an application is classified as NOT_SECURED, and has views, no mather
    if exists :class:`django_roles.models.ViewAccess` objects for those views,
    NOT_SECURED condition will take precedence over
    :class:`django_roles.models.ViewAccess` object.

------
PUBLIC
------
List of applications mainly for public access.

PUBLIC applications have their views accessibly to anonymous user except an
object of type :class:`django_roles.models.ViewAccess` exist for a view and
its configuration is more restrictive than public.

.. note::

   The behavior of views in PUBLIC applications that have other security
   challenge, will not be changed.

-------
SECURED
-------
List of applications requiring at least the user to be *Authorized*

Application classified as a SECURED application will require the user to be
logged.
