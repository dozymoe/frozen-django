from uwsgi_tasks import task, TaskExecutor
#-
from .main import generate_static_view


@task(executor=TaskExecutor.SPOOLER)
def freeze_view(view_name, base_url=None, dest=None, **kwargs):
    generate_static_view(view_name, frozen_host=base_url, frozen_dest=dest,
            **kwargs)
