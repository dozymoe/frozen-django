""" Django Command freeze_view

Build html files from selected views.

.. module:: frozen_django.management.commands.freeze_view
.. moduleauthor:: Fahri Reza <i@dozy.moe>

"""
import json
from urllib.parse import parse_qs
#-
from django.core.management.base import BaseCommand
#-
from frozen_django.main import generate_static_view

class Command(BaseCommand):
    """ Implements Command freeze_view

    Build html files from selected views.

    """
    help = "Build static html files from Django views."

    def add_arguments(self, parser):
        parser.add_argument('view_names', nargs='*', type=str, default=[])
        parser.add_argument('--base-url', action='store', dest='base_url',
                help="Specify base url (must be absolute url, ex. https://example.com/).") # pylint:disable=line-too-long
        parser.add_argument('--dest', action='store', dest='dest', default=None,
                help="Specify destination directory.")
        parser.add_argument('--params-qs', action='store', dest='params_qs',
                default='', help="Specify view arguments in query string.")
        parser.add_argument('--params-json', action='store', dest='params_json',
                default='', help="Specify view arguments in json.")


    def handle(self, *args, **kwargs):
        param_str = kwargs.get('params_qs')
        if param_str:
            params = {k: v[0] for k, v in parse_qs(param_str).items()}
        else:
            params = {}
        param_str = kwargs.get('params_json')
        if param_str:
            params.update(json.loads(param_str))

        for view_name in kwargs['view_names']:
            generate_static_view(view_name, frozen_host=kwargs['base_url'],
                    frozen_dest=kwargs['dest'], **params)
