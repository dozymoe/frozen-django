from celery import shared_task # pylint:disable=import-error
#-
from frozen_django.main import generate_static_view


@shared_task
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
