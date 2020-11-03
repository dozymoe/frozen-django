from django.conf import settings
from uwsgi_tasks import task, TaskExecutor # pylint:disable=import-error
#-
from frozen_django.main import generate_static_view


@task(executor=TaskExecutor.SPOOLER)
def freeze_view(view_name, base_url, dest=None, **kwargs):
    """
    Build html files as background task

    view_name must be fully qualified class name
              for example: website.views.Home

    base_url must be absolute url
             for example: https://example.com/
    """
    generate_static_view(view_name, frozen_host=base_url, frozen_dest=dest,
            **kwargs)


def hosts_freeze_view(view_name, dest=None, **kwargs):
    for host in settings.ALLOWED_HOSTS:
        freeze_view(view_name, base_url=host, dest=dest, **kwargs)
