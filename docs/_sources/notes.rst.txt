=====
Notes
=====

----------------
Other middleware
----------------

.. _django_algorithm: https://docs.djangoproject.com/en/dev/topics/http/urls/#how-django-processes-a-request

Django documentation explain the algorithm the system follows to determine which
Python code to execute django_algorithm_:

... but if the incoming HttpRequest object has a urlconf attribute (set by
middleware), its value will be used in place of the ROOT_URLCONF setting. ...

Django Roles *checkviewaccess* takes from ROOT_URLCONF the root for all site's
views. If an installed middleware change this root, the management command
may not work as expected.

Django Roles middleware will not change ROOT_URLCONF or any other attribute
of the HTTPRequest or HTTPResponse (except for the last one when access
denied is raised).

--------------------
Other considerations
--------------------

Why is not used user_passes_test()?
-----------------------------------

Because the callable receive the user as argument, while Django Roles also
need to know the view being accessed.



Comparatives with other solutions
---------------------------------
The main


With group_required decorator https://djangosnippets.org/snippets/1703/ is
possible to implement security with Groups. But this snippet require to
hardcoded the required group.







