# pylint:disable=missing-module-docstring,missing-function-docstring
from django.core.management.base import BaseCommand
from ..management.commands import freeze_view

def test_freeze_view():
    obj = freeze_view.Command()
    assert isinstance(obj, BaseCommand)
