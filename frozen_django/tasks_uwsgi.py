"""uwsgi-tasks implementation

For more information uwsgi-tasks visit https://pypi.org/project/uwsgi-tasks/

uwsgi-tasks uses UWSGI signal framework for asynchronous tasks management.
It's more functional and flexible than cron scheduler, and can be used as
replacement for celery in many cases.

.. module:: frozen_django.tasks_uwsgi
.. moduleauthor:: Fahri Reza <i@dozy.moe>

"""
from django.conf import settings
from uwsgi_tasks import task, TaskExecutor # pylint:disable=import-error
#-
from .main import generate_static_view


@task(executor=TaskExecutor.SPOOLER)
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
