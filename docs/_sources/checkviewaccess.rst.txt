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

   * Search for any ``django.contrib.auth.decorators``.

   * Evaluate if view is decorated with ``django_roles`` decorator or if mixin
     was used. Then is searched :class:`django_roles.models.ViewAccess`
     object for the view. And finally taking in consideration if **site_active**
     is True or not, an access security status is concluded.

5. Report from selected view will indicate:

   * View Name.

   * Declared URL.

   * Access security status.

The last of all **Access security status** is concluded by work done in step 4.

