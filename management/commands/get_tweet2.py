from django.core.management import BaseCommand

from teatwitter.teacrawler.models import KOLMaster
from teatwitter.teacrawler.tasks import extract_twitter_tweet


class Command(BaseCommand):

    def handle(self, *args, **options):
        kols = KOLMaster.objects.all()
        for kol in kols:
            extract_twitter_tweet.delay(kol.name)
