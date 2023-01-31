from django.core.management import BaseCommand
import time

from teatwitter.teacrawler.tasks import map_token_info, collection_token


class Command(BaseCommand):

    def handle(self, *args, **options):
        tokens = collection_token.find()
        tokens_ids = [str(token["id"]) for token in tokens]
        for i in range(0, len(tokens_ids), 99):
            index_str = ','.join(tokens_ids[i:i + 99])
            print(index_str)
            map_token_info.delay(index_str)
            time.sleep(1)
