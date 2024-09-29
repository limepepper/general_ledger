from django.core.management.base import BaseCommand

from django.apps import apps
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from django.apps import apps

# from general_ledger.models.account_dl_treebeard import AccountClass


class Command(BaseCommand):
    help = "do stuff here"

    def handle(self, *args, **kwargs):
        # Book.objects.all().delete()

        app_models = apps.get_app_config("general_ledger").get_models()
        for model in app_models:
            # try:
            #     admin.site.register(model)
            # except AlreadyRegistered:
            #     pass
            # print("registered", model)
            print(model._meta.db_table)
