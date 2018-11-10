============
Django Roles
============

Application for securing Django site view access by roles
(:class:`django.contrib.auth.models.Group`).

Works with:
* Django 1.11 (Python 2.7, Python 3.6)
* Django 2 (Python 3.6)

IMPORTANT:
The present application is designed for Django sites where the
*admin interface* is not commonly used; or specific *administrators* users do
their *special security reasons* task as create a new user/group or modify
them.

.. note::

   There are Django sites where the *admin interface* is used as part
   of the application for the final user, or, at least, many of them. The use
   of this application for securing the site's view access could be risky!!


Quick start
-----------
1. Install "django-roles" from pypi::

   pip install django-roles

1. Add "Roles" to your INSTALLED_APPS setting like this::

   INSTALLED_APPS = [
       ...
       'Roles',
   ]

2. Include the polls URLconf in your project urls.py like this::

   path('roles/', include('Roles.urls')),

3. Run `python manage.py migrate` to create the polls models.

4. Start the development server and visit http://127.0.0.1:8000/admin/

.. note::

   By default when you install django-roles all Django sites views keeps their
   actual *access status**. This is, if they were public, they will remain
   public. If they were restricted by some logic (like
   :func:`django.contrib.auth.decorators.login_required`), they will remain
   restricted by the same logic.


Quick security
--------------

Mainly django-roles is about setting roles access to views. This is done in
Admin creating an :class:`ViewAccess` object for each view. There are 3
possible type of access to be set:
* Public: Any user can access the view.
* Authorized: Only authorized :class:`django.contrib.auth.User` can access
  the view. Is equivalent to
  :func:`django.contrib.auth.decorators.login_required`.
* By roles: Only :class:`django.contrib.auth.User` belonging to
  :class:`django.contrib.auth.Group` that has been granted access to the
  view can access the view.

django-roles classifies Django site applications in three groups:
* NO_SECURED: List of applications not under site security.
* PUBLIC: List of applications mainly for public access.
* SECURED: List of applications must be secured their view access by roles (
:class:`django.contrib.auth.Group`).

By default if any of this 3 variables are declared in *settings* all
applications will be assumed as public, and their view also as public.

Quick access configuration
--------------------------

Quick access configuration in two steps.

.. note::

   For a quick access configuration all application will leave as public
   (default behavior). This is no more configuration in settings than add
   Roles application.

Step 1
~~~~~~

In Admin add a new :class:`ViewAccess` object:
1. In **view** select the view you want to secure.
2. In **type** select the type of access you want for the view.
3. If you select *By role* access type, add to **roles** the
   :class:`django.contrib.auth.Group` who's members you want to grant access
   to the view.

Step 2
~~~~~~

The second step is about using :func:`Role.decorators.access_by_role` decorator
to decorate the view you want to secure (The selected in Step 1).
For example:::

In case the view is a function:::

    from roles.decorators import access_by_role

    @access_by_role()
    myview(request):
       ...


Or in case of classes:::

    from django.utils.decorators import method_decorator
    from roles.decorators import access_by_role

    class MyView(View):

        ...


        @method_decorator(access_by_role)
        def dispatch(self, *args, **kwargs):
            return super(MyView, self).dispatch(*args, **kwargs)