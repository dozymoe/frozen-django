"""celery implementation

For more information about celery tasks visit
https://docs.celeryproject.org/en/stable/django/first-steps-with-django.html

Celery is a simple, flexible, and reliable distributed system to process vast
amounts of messages, while providing operations with the tools required to
maintain such a system.

It's a task queue with focus on real-time processing, while also supporting
task scheduling.

.. module:: frozen_django.tasks_celery
.. moduleauthor:: Fahri Reza <i@dozy.moe>

"""
from celery import shared_task # pylint:disable=import-error
from django.conf import settings
#-
from .main import generate_static_view


@shared_task
def freeze_view(view_name, base_url, dest=None, **kwargs):
    """Build html files as background tasks

    :param view_name: Fully qualified name of view
    :type view_name: str.
    :param base_url: Host information prepended to the url, must be absolute url
    :type base_url: str.
    :param dest: Output directory where the files will be stored.
    :type dest: str.

    .. note::

       An example of view_name: website.views.Home

       An example of base_url: https://example.com/

    """
    generate_static_view(view_name, frozen_host=base_url, frozen_dest=dest,
            **kwargs)


def hosts_freeze_view(view_name, dest=None, **kwargs):
    """Build html files for all listed in ALLOWED_HOSTS

    :param view_name: Fully qualified name of view
    :type view_name: str.
    :param dest: Output directory where the files will be stored.
    :type dest: str.

    .. note::

       An example of view_name: website.views.Home

    """
    for host in settings.ALLOWED_HOSTS:
        freeze_view(view_name, base_url=host, dest=dest, **kwargs)
