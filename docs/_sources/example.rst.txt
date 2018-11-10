---------------
Tutorial Part 1
---------------

.. _create-example-django-project:

Create example Django project
-----------------------------
This tutorial will explain how to use Django-Roles. For this is necessary a
simple Django project and application. With the spirit of standard this
tutorial use Django's documentation *polls* example. This example can be found
at Django_example_.

.. _Django_example: https://docs.djangoproject.com/en/2.0/intro/tutorial01/

.. _create-proyect-and-application:

1 Create project and application
================================
Start by creating a Django project:::

    django-admin startproject mysite

Once the project has been created, proceed to create a new application:::

    cd mysite
    python manage.py startapp polls

Now there are Django project and application. Let write some simple code. First
 step will be to add *myapp* to :setting:`INSTALLED_APPS`

.. code-block:: django
   :caption: mysite/settings.py
   :name: mysite-settings-py

   INSTALLED_APPS = [
       ...
       'polls',
   ]

.. _create-example-models:

2 Create examples models
========================
In *models.py* in *polls* folder add the code used by Django project in polls
example:

.. code-block:: django
   :caption: polls/models.py
   :name: polls-models-py

   import datetime

   from django.db import models
   from django.utils import timezone


   class Question(models.Model):
       question_text = models.CharField(max_length=200)
       pub_date = models.DateTimeField('date published')

       def __str__(self):
           return self.question_text

       def was_published_recently(self):
           return self.pub_date >= timezone.now() - datetime.timedelta(days=1)


   class Choice(models.Model):
       question = models.ForeignKey(Question, on_delete=models.CASCADE)
       choice_text = models.CharField(max_length=200)
       votes = models.IntegerField(default=0)

       def __str__(self):
           return self.choice_text

.. _create-example-views:

3 Create examples views
=======================
In *views.py* in *polss* folder add the code used by Django project in polls
example:

.. code-block:: django
   :caption: polls/views.py
   :name: polls-views-py

   from django.http import HttpResponseRedirect
   from django.shortcuts import get_object_or_404, render
   from django.urls import reverse
   from django.views import generic

   from .models import Choice, Question


   class IndexView(generic.ListView):
       template_name = 'polls/index.html'
       context_object_name = 'latest_question_list'

       def get_queryset(self):
           """Return the last five published questions."""
           return Question.objects.order_by('-pub_date')[:5]


   class DetailView(generic.DetailView):
       model = Question
       template_name = 'polls/detail.html'


   class ResultsView(generic.DetailView):
       model = Question
       template_name = 'polls/results.html'


   def vote(request, question_id):
       question = get_object_or_404(Question, pk=question_id)
       try:
           selected_choice = question.choice_set.get(pk=request.POST['choice'])
       except (KeyError, Choice.DoesNotExist):
           # Redisplay the question voting form.
           return render(request, 'polls/detail.html', {
               'question': question,
               'error_message': "You didn't select a choice.",
           })
       else:
           selected_choice.votes += 1
           selected_choice.save()
           # Always return an HttpResponseRedirect after successfully dealing
           # with POST data. This prevents data from being posted twice if a
           # user hits the Back button.
           return HttpResponseRedirect(reverse('polls:results',
                                               args=(question.id,)
                                              ))

.. _configure-urlconf:

4 Configure URLConf
===================
Update *mysite/urls.py* to have next code:

.. code-block:: django
   :caption: mysite/urls.py
   :name: mysite-urls-py

   from django.contrib import admin
   from django.urls import include, path

   urlpatterns = [
       path('polls/', include('polls.urls')),
       path('admin/', admin.site.urls),
   ]

Create a new file in *polls* directory with the name *urls.py* and copy the
content from the example in Django documentations.

.. code-block:: django
   :caption: polls/urls.py
   :name: polls-urls-py

   from django.urls import path

   from . import views

   app_name = 'polls'
   urlpatterns = [
       path('', views.IndexView.as_view(), name='index'),
       path('<int:pk>/', views.DetailView.as_view(), name='detail'),
       path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
       path('<int:question_id>/vote/', views.vote, name='vote'),
   ]

.. _configure-for-admin-site:

5 Configure for Admin site
==========================
In *polls/admin.py* add the next code:

.. code-block:: django
   :caption: polls/admin.py
   :name: polls-admin-py

   from django.contrib import admin
   from .models import Question, Choice

   admin.site.register(Question)
   admin.site.register(Choice)

I modify this so you can add Choice in the admin.

.. _create-templates:

6 Create templates
==================
Create directory *polls/templates/polls* and add next html files:

.. code-block:: django
   :caption: polls/templates/polls/index.html
   :name: polls-templates-polls-index-html

   {% if latest_question_list %}
     <ul>
       {% for question in latest_question_list %}
         <li>
           <a href="/polls/{{ question.id }}/">{{ question.question_text }}</a>
         </li>
       {% endfor %}
     </ul>
   {% else %}
     <p>No polls are available.</p>
   {% endif %}


.. code-block:: django
   :caption: polls/templates/polls/detail.html
   :name: polls-templates-polls-detail-html

   <h1>{{ question.question_text }}</h1>

   {% if error_message %}<p><strong>{{ error_message }}</strong></p>{% endif %}

     <form action="{% url 'polls:vote' question.id %}" method="post">
       {% csrf_token %}
         {% for choice in question.choice_set.all %}
           <input type="radio" name="choice" id="choice{{ forloop.counter }}"
             value="{{ choice.id }}" />
           <label for="choice{{ forloop.counter }}">{{ choice.choice_text }}
           </label>
           <br />
         {% endfor %}
       <input type="submit" value="Vote" />
   </form>


.. code-block:: django
   :caption: polls/templates/polls/results.html
   :name: polls-templates-polls-results-html

   <h1>{{ question.question_text }}</h1>

   <ul>
     {% for choice in question.choice_set.all %}
       <li>
         {{ choice.choice_text }} -- {{ choice.votes }} vote{{ choice.votes|pluralize }}
       </li>
     {% endfor %}
   </ul>

   <a href="{% url 'polls:detail' question.id %}">Vote again?</a>

.. _example-installing-django-roles:

Installing Django-Roles
-----------------------
Download Django-Roles from PyPi with the command:::

    pip install django-roles

Once installed proceed to added to :setting:`INSTALLED_APPS`.



