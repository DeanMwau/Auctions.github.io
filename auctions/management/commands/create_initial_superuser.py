from django.core.management.base import BaseCommand
from auctions.models import User
import os

class Command(BaseCommand):
    help = 'Creates an initial superuser if one does not exist'

    def handle(self, *args, **options):
        username = os.environ['DJANGO_SUPERUSER_USERNAME']
        password = os.environ['DJANGO_SUPERUSER_PASSWORD'] 
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL') 

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username, email, password)
            self.stdout.write(self.style.SUCCESS(f'Successfully created superuser: {username}'))
        else:
            self.stdout.write(self.style.WARNING(f'Superuser {username} already exists.'))