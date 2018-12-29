==========
Middleware
==========

In Pro of simplicity Django Roles think in cases where all applications or
views should have access. For example the user need to be logged-in to access
the views, and you want this behavior by default. The cleanest way (the state of
the art?) to achieve this is through the use of a middleware.