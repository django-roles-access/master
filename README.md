#![Django roles access](django-roles-access.png "Django roles access") Django Roles Access 
![](https://img.shields.io/badge/release-v0.9.0-blue.svg)
![](https://img.shields.io/badge/state-stable-brightgreen.svg)
[![Build Status](https://travis-ci.org/django-roles-access/master.svg?branch=master)](https://travis-ci.org/django-roles-access/master)
[![codecov](https://codecov.io/gh/django-roles-access/master/branch/master/graph/badge.svg)](https://codecov.io/gh/django-roles-access/master)


Application for securing access to views with roles
(*Django contrib Groups*).

**django_roles_access** is a Django app for securing access to views. It's
built on top of *Django contrib Groups* interpreted as role. The objective of
the app are:

* Provide secure access to views.

* Be able to administrate access to views without the need to restart the
  server (at run time).

* Minimize the need of new code, or eliminate it at all (when using
  **django_roles_access** middleware). Also free developers from the task 
  of coding any view access.

* **django_roles_access** also provides a security report by registering
  **checkviewaccess** action.

Works with:

* Django 1.10+ (Python 2.7, Python 3.5+)

* Django 2 (Python 3.5+)

* [Documentation](https://django-roles-access.github.io)


## Requirements


Django roles access use *Django contrib Groups*, *Django contrib User*. Also
*Django
admin interface* is necessary to create and administrate *views access*
([django_roles_access.models.ViewAccess](https://django-roles-access.github.io/reference.html#django_roles_access.models.ViewAccess)).
So Django roles access is dependent of *Django admin site* and because of
this it has the same requirements than it. This can be checked in the
[official documentation:](https://docs.djangoproject.com/en/dev/ref/contrib/admin/)


## Quick start


### Installation and configuration


1. Install **django_roles_access** from pypi:


    pip install django-roles-access

2. Add **'django_roles_access'** to your INSTALLED_APPS setting:
    
    
    INSTALLED_APPS = [
        ...
        'django_roles_access',
    ]
    
3. Run migrations to create the **django_roles_access** models:


    python manage.py migrate


>Note:
>
>   If nothing else is done, then Django site security keeps without
>   modification.


### Access configuration


Quick view access configuration in two steps.

#### Step 1


In *Django admin* interface create a 
[django_roles_access.models.ViewAccess](https://django-roles-access.github.io/reference.html#django_roles_access.models.ViewAccess)
object and configure it:

1. **view** attribute: name of the view you to be secured. Format used: 
   `<app_name:view_name>`(
   [Namespaces and View name](https://django-roles-access.github.io/advanced.html#namespaces-and-view-name)).

2. **type** attribute: select the *access type* for the view:

   * **Public**: Any visitor can access the view.

   * **Authorized**: Only authorized (logged) *Django contrib User* can access
     the view.

   * **By roles**: Only *Django contrib User* belonging to any added *Django 
   contrib user* will access the view.

3. **roles** attribute: When *By roles* is selected as *access type*, this
   attribute hold any *Django contrib Group* whose members will access the view.


#### Step 2

In the view to be secured use: 

* **access_by_roles** decorator in case of view function
  ([django_roles_access.decorators.access_by_roles](https://django-roles-access.github.io/reference.html#django_roles_access.decorator.check_view_acces)) 
  
* **RolesMixin** mixin in case of classes based views
  ([django_roles_access.mixin.RolesMixin](https://django-roles-access.github.io/reference.html#django_roles_access.mixin.RolesMixin)) 

For example:

In case of view is a function:


    from django_roles_access.decorators import access_by_role

    @access_by_role()
    myview(request):
       ...


In case of classes based views use mixin:


    from django_roles_access.mixin import RolesMixin

    class MyView(RolesMixin, View):

        ...


>Note:
>
>   When user has no access to a view, by default **django_roles_access**
>   response with *django.http.HttpResponseForbidden*.

>Warning:
>
>   Pre existent security behavior can be modified if a **django_roles_access**
>   configuration for the same view results in a more restricted view access.


## Test Django roles access

You can check the **django_roles_access** test execution at 
[Travis CI integration](https://travis-ci.org/django-roles-access/master)
([![Build Status](https://travis-ci.org/django-roles-access/master.svg?branch=master)](https://travis-ci.org/django-roles-access/master))

You can also check **dajngo_roles_access** test coverage at
[Coverage](https://django-roles-access.github.io/coverage.html)
([![codecov](https://codecov.io/gh/django-roles-access/master/branch/master/graph/badge.svg)](https://codecov.io/gh/django-roles-access/master))

Or:

1. Create a virtual environment.

2. Get into and activate virtual environment.

3. Clone **django_roles_access**:


    git clone https://github.com/django-roles-access/master.git


2. Install tox:


    pip install tox


3. Run the tests:


    tox


## Related sites

* [Documentation](https://django-roles-access.github.io)

* [Package at pypi.org](https://pypi.org/project/django-roles-access/)

* [source code](https://github.com/django-roles-access/master)

* [Travis CI integration](https://travis-ci.org/django-roles-access/master)

* [Codecov](https://codecov.io/gh/django-roles-access/master)

