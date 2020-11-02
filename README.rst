FROZEN DJANGO
=============

Export webpages created by your Django views into html files.

It is dumb, it won't deploy the files to AWS for instance, and won't collect
assets from static files or media files.

The assumption is that the build process will be triggered by Django signals,
for example when a BlogPost was created, and will only rebuild the related
html (or json) files.

Inspired by:

* django-bakery_
* django-distill_


Requirements
------------

* add `frozen_django` to your `INSTALLED_APPS`
* will only process named urls
* will only process urls with file extensions (.html, .json, .js, .xml, etc.)
* Django Views with pagination must have **Link** HTTP header or
  html tag `<link rel="next" />` in their content


Settings
--------

* FROZEN_ROOT (should be filled)
* FROZEN_MIDDLEWARE (optional)


API
---

* Django Command `freeze_view`
* uwsgi task `freeze_view`


Examples
--------

Here is an example of all pages rebuild:

File novel/urls.py:

.. code-block:: python

    from django.urls import path
    #-
    from novel_serie.views import ViewSerie
    from website import views

    urlpatterns = [
        path('<str:slug>.<str:format>', ViewSerie.as_view(), name='DisplaySerie'),
        path('index.html', views.Home.as_view(), name='Home'),
    ]


File website/views.py

.. code-block:: python

    from django.views.generic import ListView
    #-
    from novel_serie.models import Serie

    class Home(ListView):
        template_name = 'website/home.html'
        paginate_by = 2

        def get_queryset(self):
            return Serie.objects.all()


File website/management/commands/build.py

.. code-block:: python

    from django.conf import settings
    from django.core.management.base import BaseCommand
    from frozen_django.tasks_uwsgi import freeze_view
    #-
    from novel_serie.models import Serie

    class Command(BaseCommand):
        help = "Build static html files."

        def build(self, view_name, **kwargs):
            for host in settings.ALLOWED_HOSTS:
                freeze_view(view_name, base_url=host, **kwargs)

        def handle(self, *args, **kwargs):
            self.build('website.views.Home') # will also build pages.

            for obj in Serie.objects.all():
                self.build('novel_serie.views.ViewSerie', slug=obj.slug,
                        format='html')


.. _django-bakery: https://pypi.org/project/django-bakery/
.. _django-distill: https://pypi.org/project/django-distill/
