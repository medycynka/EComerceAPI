from django.core.management.base import BaseCommand


from API import factories


class Command(BaseCommand):
    help = "Create fake db data for testing"
    requires_system_checks = ()
    skip_checks = True

    def add_arguments(self, parser):
        parser.add_argument('batch_size', nargs=1, type=int)
        parser.add_argument('-ub', '--user_batch_size', nargs=1, type=int, default=0)
        parser.add_argument('-u', '--users', action='store_true', default=False)
        parser.add_argument('-oo', '--only_orders', action='store_true', default=False)

    def handle(self, *args, **options):
        if options['users']:
            self.stdout.write(self.style.SUCCESS(f'Generating {int(int(options["user_batch_size"][0]))} test users...'))
            factories.UserFactory.create_batch(int(int(options['user_batch_size'][0])))
            self.stdout.write(self.style.SUCCESS(
                f'Successfully created {int(int(options["user_batch_size"][0]))} test users.'
            ))

        batch_size = int(int(options['batch_size'][0]))

        if not options['only_orders']:
            self.stdout.write(self.style.SUCCESS(f'Generating {batch_size} test categories...'))
            factories.CategoryFactory.create_batch(batch_size)
            self.stdout.write(self.style.SUCCESS(f'Successfully created {batch_size} test categories.'))

            self.stdout.write(self.style.SUCCESS(f'Generating {batch_size} test products...'))
            factories.ProductFactory.create_batch(batch_size)
            self.stdout.write(self.style.SUCCESS(f'Successfully created {batch_size} test products.'))

        self.stdout.write(self.style.SUCCESS(f'Generating {batch_size} test orders...'))
        factories.OrderFactory.create_batch(batch_size)
        self.stdout.write(self.style.SUCCESS(f'Successfully created {batch_size} test orders.'))

        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully created all test data.\n'))
