=================
Check view access
=================

Django roles register an action with manage.py:
::

    python manage.py checkviewaccess

This action will analyze all reachable views from settings.ROOT_URLCONF and
print to standard output a *security report* of access to each view.


.. _django_algorithm: https://docs.djangoproject.com/en/dev/topics/http/urls/#how-django-processes-a-request

.. warning::

   Django documentation explain the algorithm the system follows to determine
   which Python code to execute django_algorithm_:

   ... but if the incoming HttpRequest object has a urlconf attribute (set by
   middleware), its value will be used in place of the ROOT_URLCONF setting.
   ...

   Django Roles *checkviewaccess* takes from ROOT_URLCONF the root for all
   site's views. If an installed middleware change this root, registered
   action may not work as expected.

.. note::

   Django Roles middleware do not change ROOT_URLCONF or any other attribute
   of the HTTPRequest. HTTPResponse is changed only when access denied is
   raised.

--------------
Roles security
--------------

It is also possible to use ``checkviewaccess`` using a role name (
:class:`django.contrib.auth.models.Group` name) for getting all views where
such role have access:
::

    python manage.py checkviewaccess <role_name>


--------------
Views security
--------------

If in place of role name, ``checkviewaccess`` is used with a view name, It
will report the configured access to the view (configured with Django roles
tools):
::

    python manage.py checkviewaccess <view_name>


--------
Analysis
--------

The used analysis follow next algorithm:

1. All views are collected and grouped by application. In the created report
   this step si called **gathering information**.

2. Is checked if Django roles middleware is active or not. When active the
   report will indicate **Django roles active for site: True**. When not
   active it will br reported as **Django roles active for site: False**. Also
   analysis will keep track of this state in it's **site_active** variable.

3. For each installed application (settings.INSTALLED_APPLICATION) is checked
   if the application was classified as explained in
   :ref:`Applications type`. The result of this is reported to standard output.

4. For each view of the analyzed application selected in step 3, is checked
   the access security by analyzing the callable associated with the view. This
   analysis include:

   * Evaluate if view is decorated with ``django_roles`` decorator, or if mixin
     was used.

   * Search any :class:`django_roles.models.ViewAccess` object for the view.

   * Take in consideration if **site_active** is True or not.

   * Take in consideration the :ref:`Applications type` of the application
     holding the view.

5. Report from selected view will indicate:

   * View Name.

   * Declared URL.

   * Access security status.

------
Method
------

The used method to determine **Access security status** of a view is:

1. A :class:`django_roles.models.ViewAccess` object is searched for the view.

2. If **site_active** is True:

   a. If an object was found in step 1, object security is reported for the
      view. If object security is type `By role` and no roles were added an
      ERROR is reported (no one, except superuser, can access de view).

   b. If no object was found; default behavior for view's application is
      reported as explained in :ref:`Applications type`.

   c. If no object was found in step 1. And no application type is
      defined for view's application (or view has no application defined). An
      ERROR of configuration is reported.

3. If **site_active** is False and ``django_roles`` decorator or mixin was used:

   a. In case exist object found in step 1, object security is reported.

   b. In case no object were found in step 1. And view's application has a
      type as defined in :ref:`Applications type`. Default behavior for the
      application type is reported as view access security.

   c. In case no object were found in step 1. And no application type is
      defined for view's application (or view has no application defined). An
      ERROR of configuration is reported.
