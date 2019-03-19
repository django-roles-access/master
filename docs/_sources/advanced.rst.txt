.. _`Required views and app name`:

===========================
Required views and app name
===========================

One last requirement is to give names in *urls.py* files to views and
applications.

This is an implicit requirement if is expected to use all
``django_roles_access`` characteristics. This is necessary because the value
used by ``django_roles_access`` to identify the views to be protected is it's
name. Equally is necessary to name the app with ``app_name``. Examples of
this can be found in Django project tutorial at `Namespacing URL names`_.

As with Django this requirement could be optional; but if it is planned to
create :class:`django_roles_access.models.ViewAccess` object for a view, will be
necessary to have a way to name the view so the object can be associated with
it.

In the same way, if it is planned to classify applications in different types as
is explained in :ref:`Applications type` it will be necessary to name the
application in *urls.py file*.

.. _`Namespacing URL names`: https://docs.djangoproject.com/en/dev/intro/tutorial03/#namespacing-url-names

.. warning::

   ``django_roles_access`` use views names to associate
   :class:`django_roles_access.models.ViewAccess` objects to the named view. And
   applications names to group all views belonging to that application so is
   possible to configure a type for the application and give it's views a
   default security behavior.


.. _`Namespace and View Name`:

========================
Namespaces and View Name
========================

When creating a :class:`django_roles_access.models.ViewAccess` object, the
value of **view** attribute can be:

* `view_name`
* `app_name:view_name`
* `namespace:view_name`
* `nest_namespace:namespace:view_name`

As this are the only possible value for **view** attribute, a requirement of
``django_rolesdjango_roles_access`` is to use *view names* and *app_name* in
*urls.py* files. Read more about Naming URL in official Django project
documentation `Naming URL`_.

.. _`Naming URL`: https://docs.djangoproject.com/en/dev/topics/http/urls/#naming-url-patterns


============================
Django roles access response
============================

When a user try to access a view and result a forbidden action, is possible
to setup different responses to user.

----------------------------
DJANGO_ROLES_ACCESS_REDIRECT
----------------------------

By default ``django_roles_access`` response with
:class:`django.http.HttpResponseForbidden` when the user has no access to the
view. This behavior can be changed if add in *settings files* a new
attribute `DJANGO_ROLES_ACCESS_REDIRECT` with a value equal to True:
::

    ...
    DJANGO_ROLES_ACCESS_REDIRECT = True
    ...

The answer given to a user without access is a
:class:`django.http.HttpResponseRedirect` to the address configured in
*settings.LOGIN_URL*.

-------------------------------------
DJANGO_ROLES_ACCESS_FORBIDDEN_MESSAGE
-------------------------------------

When ``django_roles_access`` answer with HttpResponseForbidden, the message
used by default is: ``<h1>403 Forbidden</h1>``; but this configuration can
also be changed if add in *settings files* a new attribute
`DJANGO_ROLES_ACCESS_FORBIDDEN_MESSAGE` with the wanted message to be returned
instead of default one.