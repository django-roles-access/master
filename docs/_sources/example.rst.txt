=======
Example
=======

.. _create-example-django-project:

---------------------------------
1 Create Django project polls app
---------------------------------

This example show quickly how to apply ``django_roles``. As is necessary a
simple Django project and application, this example use Django's
documentation *polls app* example for this. This example can be found
at Django_example_.

.. _Django_example: https://docs.djangoproject.com/en/dev/intro/tutorial01/


.. note::

   This example assume you have all the code of *polls app*.

--------------------
2 App and views name
--------------------

.. _`writing more views`: https://docs.djangoproject.com/en/dev/intro/tutorial03/#namespacing-url-names

Make sure you name views in *polls/urls.py* as in example you can found in
`writing more views`_. Also note how ``app_name = 'polls'`` is configured.


------------------------------
3 Start using ``django_roles``
------------------------------

Imagine you want to keep polls application public, in this way all users
(anonymous or not) can vote a polls; but result should be restricted to a
special users with specific role.

Achieve this is very simple with ``django_roles``:

* Install ``django_roles`` middleware; or add ``django_roles`` decorators to
  *results* views

  .. code-block:: python
      :caption: polls/views.py

      ...
      from django_roles.decorator import access_by_role
      ...

      @access_by_role
      def results(request, question_id):
          response = "You're looking at the results of questions %s."
          return HttpResponse(response % question_id)

* Go to *admin site*.

* Create a new :class:`django_roles.models.ViewAccess` configure it:

  * **view** attribute: Type ``polls:results``.

  * **type** attribute: Select ``By role``.

  * **role** attribute: Add :class:`django.contrib.auth.models.Group`
    representing the specific role.

If new users need access to the view, you only need to add that user to the
any of the groups added to **roles** attributes. This can be done in run time
from *admin site*.

.. note::

   Is not nice at all to receive 403 Forbidden after voting!!!. A simple code
   modification could help:

   .. code-block:: python
       :caption: polls/views.py

       ...

       def vote(...

           ...

           return HttpResponseRedirect(reverse('polls:index'))

