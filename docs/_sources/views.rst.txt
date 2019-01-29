=====
Views
=====

-------------------------------
1 Configure applications access
-------------------------------


------------------------
2 Configure views access
------------------------

-------------------
3 Decorate the view
-------------------

-----------
4 Use Mixin
-----------

5 Delete


.. _basic-concepts:

--------------
Basic concepts
--------------
Django Roles implements it's core *roles* with
:class:`django.contrib.auth.models.Group`. This means that
:mod:`django.contrib.auth` must be listed in :django:setting:`INSTALLED_APPS`.

This could be an extra effort if you just want to grant a
:class:`django.contrib.auth.models.User` access to a view.
For example in case where only a particular user must be the only one in
access a particular view. To solve this you can create a new
:class:`django.contrib.auth.models.Group` and named it in such a way you
reflect this particular case.

In general there are, from security point of view, two kind of applications:

* **Simple**: This kind of sites requires user to be logged in some views.
  This is the case when @login_required is used.

* **Heavy**: This kind of sites requires user to be logged in almost all
  views. The use of @login_required became impractical or at least tedious.

Django Roles could work in to ways depending in site's security requirements
as explained: simple or heave:

* **With function/decorator**: For this cases Django Roles provides a
  decorator or function to check security.

* **With middleware**: When a site requires user to be logged in almost all
  views. Django Roles offers a middleware to free you of the need of using the
  mentioned decorator.

For any of the cases (function/decorator or middleware) Django Roles is used
equally.
