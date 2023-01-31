from django.core.management import BaseCommand

from teatwitter.teacrawler.tasks import get_all_token


class Command(BaseCommand):

    def handle(self, *args, **options):
        get_all_token.delay()
