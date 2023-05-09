from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create custom users groups for managing project's endpoints authentications"

    def handle(self, *args, **options):
        for group_name in settings.USERS_CUSTOM_GROUPS:
            Group.objects.get_or_create(name=group_name)

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created custom groups: {", ".join(settings.USERS_CUSTOM_GROUPS)}')
        )
