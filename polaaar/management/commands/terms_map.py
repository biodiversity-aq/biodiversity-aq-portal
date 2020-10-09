import datetime
import os

from django.core.management.base import BaseCommand, CommandError
from django.apps import apps


class Command(BaseCommand):
    help = 'Generate field names definition'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        app_models = apps.get_app_config('polaaar').get_models()
        file_name = os.path.join('polaaar', 'static', 'polaaar', 'terms_map.txt')
        with open(file_name, 'w+') as writer:
            writer.write('table\tfield\tdefinition\n')
            for model in app_models:
                if model._meta.model_name in ['mailfile', 'projectfiles']:
                    continue
                table = model._meta.model_name
                for field in model._meta.fields:
                    field_name = '{}'.format(field.name)
                    definition = '{}\n'.format(field.help_text)
                    line = "\t".join([table, field_name, definition])
                    writer.write(line)
            version = "generated on {}".format(datetime.datetime.now().isoformat())
            writer.write(version)
