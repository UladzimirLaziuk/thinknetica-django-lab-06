from django.core.management.base import BaseCommand, CommandError
import importlib

MAP_DICT = {'User': 'UserFactory',
            'Seller': 'SellerFactory',
            'Tag': 'TagFactory',
            'Ad': 'AdFactory',
            'Category': 'CategoryFactory'
            }


def func_get_count(args):
    count = args[-1]
    if not count.isdigit():
        count = 1
    return count


class Command(BaseCommand):
    help = 'creating models for tests: input ' \
           'example "nameModel"=4'

    def add_arguments(self, parser):
        parser.add_argument("--model", '-model', action='append',
                            type=lambda data: data.split("="), dest='model')

    def handle(self, *args, **options):
        print(options)
        for model_in_list in options.get('model'):
            try:
                name_models = model_in_list[0]
                name_model_factory = MAP_DICT.get(name_models)
                mod = importlib.import_module("shop_site.factory_boy")
                model_factory = getattr(mod, name_model_factory)
                count = func_get_count(model_in_list)
                model_factory.create_batch(int(count))
            except Exception:
                raise CommandError('failed to create model "%s"' % name_models)

            self.stdout.write(self.style.SUCCESS('Successfully create model "%s"' % name_models))
