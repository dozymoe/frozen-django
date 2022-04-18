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

* add ``frozen_django`` to your ``INSTALLED_APPS``
* will only process urls with file extensions (.html, .json, .js, .xml, etc.)
* Django Views with pagination must have **Link** HTTP header or
  html tag ``<link rel="next" />`` in their content


Settings
--------

* FROZEN_ROOT (should be filled, can be dict for multisite, keys are
  items in ALLOWED_HOSTS)
* FROZEN_MIDDLEWARE (optional)


API
---

* Django Command ``freeze_view``
* ``frozen_django.tasks_celery.freeze_view``
* ``frozen_django.tasks_uwsgi.freeze_view``


Examples
--------

Here is an example of all pages rebuild:

File blog/settings.py

.. code:: python

    from django.utils.translation import gettext_lazy as _

    ALLOWED_HOSTS = ['www.blog.id', 'www.planet.id']

    INSTALLED_APPS = [
        'frozen_django',
    ]

    MIDDLEWARE = [
        'django.middleware.locale.LocaleMiddleware',
        'django.contrib.sites.middleware.CurrentSiteMiddleware',
    ]

    FROZEN_MIDDLEWARE = [
        'django.middleware.locale.LocaleMiddleware',
        'django.contrib.sites.middleware.CurrentSiteMiddleware',
    ]

    USE_I18N = True
    LANGUAGE_CODE = 'en'

    LANGUAGES = (
        ('en', _("English")),
        ('id', _("Bahasa Indonesia")),
    )

    FROZEN_ROOT = {
        'www.blog.id': ROOT_DIR/'public'/'blog',
        'www.planet.id': ROOT_DIR/'public'/'planet',
    }


File blog/urls.py:

.. code:: python

    from django.conf.urls.i18n import i18n_patterns
    from django.utils.translation import gettext_lazy as _
    from website import views

    urlpatterns = i18n_patterns(
        path(_('posts/'), include('blog_post.urls', namespace='blogpost')),
        path('index.<str:format>', views.Home.as_view(), name='home'),
        path('index/pages/<int:page>.<str:format>', views.Home.as_view(),
            name='homepages'),
        prefix_default_language=True,
    )


File blog_post/urls.py:

.. code:: python

    from . import views

    app_name = 'blog_post'

    urlpatterns = [
        path('<str:slug>.<str:format>', views.Display.as_view(), name='display'),
    ]


File blog_post/signals.py

.. code:: python

    from website.tasks import hosts_freeze_view

    def post_updated(sender, instance, **kwargs):
        hosts_freeze_view('website.views.Home', format='html')
        hosts_freeze_view('blog_post.views.Display', slug=instance.slug,
                format='html')


File blog_post/apps.py

.. code:: python

    from django.db.models.signals import post_save

    class BlogPostConfig(AppConfig):
        name = 'blog_post'

        def ready(self):
            from . import models
            from .signals import post_updated

            post_save.connect(post_updated, sender=models.BlogPost)


File website/views.py

.. code:: python

    from django.views.generic import ListView
    #-
    from blog_post.models import Post

    class Home(ListView):
        template_name = 'website/home.html'
        paginate_by = 2

        def get_queryset(self):
            return Post.objects.all()


File website/tasks.py

.. code:: python

    from django.conf import settings
    from frozen_django.main import generate_static_view
    from uwsgi_tasks import task, TaskExecutor

    @task(executor=TaskExecutor.SPOOLER)
    def freeze_view(view_name, base_url, **kwargs):
        generate_static_view(view_name, frozen_host=base_url, **kwargs)


    def hosts_freeze_view(view_name, **kwargs):
        for host in settings.ALLOWED_HOSTS:
            freeze_view(view_name, base_url=host, **kwargs)


File website/templates/website/home.html

.. code:: html

      <html>
        <head>
          {% if page_obj.has_next %}
            <link rel="next" href="{% url 'homepages' page=page_obj.next_page_number format='html' %}">
          {% endif %}
        </head>
      </html>


.. _django-bakery: https://pypi.org/project/django-bakery/
.. _django-distill: https://pypi.org/project/django-distill/
