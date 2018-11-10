Notes
-----

Why is not used user_passes_test()?
Because the callable receive the user as argument, while access by role also
need to know the view being accessed. As pure decorator it receive the request.



Comparatives with other technology

With group_required decorator https://djangosnippets.org/snippets/1703/ is
possible to implement security with Groups. But this snippet require to
hardcode the required group.
Django-roles lets administrate the security dynamically with ViewAccess objects.