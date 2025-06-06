from django.core.cache import cache
from django.core.management import BaseCommand
from django.db.utils import OperationalError
import time

class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('Waiting for redis...')

        cache.clear()

        self.stdout.write(self.style.SUCCESS('Cache has been cleared!'))
