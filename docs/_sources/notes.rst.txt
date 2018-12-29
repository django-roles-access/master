Notes
-----



How Django processes a request

1) Django determines the root URLconf module to use. Ordinarily, this is the
value of the ROOT_URLCONF setting, but if the incoming HttpRequest object has a
urlconf attribute (set by middleware), its value will be used in place of the
ROOT_URLCONF setting.

2) Django loads that Python module and looks for the variable urlpatterns. This
 should be a Python list of django.urls.path() and/or django.urls.re_path()
 instances.

3) Django runs through each URL pattern, in order, and stops at the first one
that matches the requested URL.

4) Once one of the URL patterns matches, Django imports and calls the given
view, which is a simple Python function (or a class-based view). The view gets
passed the following arguments:
An instance of HttpRequest.
If the matched URL pattern returned no named groups, then the matches from the
regular expression are provided as positional arguments.
The keyword arguments are made up of any named parts matched by the path
expression, overridden by any arguments specified in the optional kwargs
argument to django.urls.path() or django.urls.re_path().

5) If no URL pattern matches, or if an exception is raised during any point in
this process, Django invokes an appropriate error-handling view. See Error
handling below.




Why is not used user_passes_test()?
Because the callable receive the user as argument, while access by role also
need to know the view being accessed. As pure decorator it receive the request.



Comparatives with other technology

With group_required decorator https://djangosnippets.org/snippets/1703/ is
possible to implement security with Groups. But this snippet require to
hardcode the required group.
Django-roles lets administrate the security dynamically with ViewAccess objects.