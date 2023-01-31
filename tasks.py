import datetime
import json
import pymongo
import snscrape.modules.twitter as snstwitter
from pymongo.errors import BulkWriteError
from config import celery_app
from django.conf import settings
from coinmarketcapapi import CoinMarketCapAPI
from celery.signals import task_success

my_client = pymongo.MongoClient(settings.DB_NAME)
dbname = my_client['twittertool']
collection_name = dbname["tweet"]
collection_token = dbname["token"]
collection_tweet_user = dbname["tweet_user"]
collection_celery_task = dbname["celery_task"]
cmc = CoinMarketCapAPI(settings.COIN_MARKET_CAP_API_KEY)


@celery_app.task()
def extract_twitter_tweet(account_name: str):
    """A pointless Celery task to demonstrate usage."""

    def datetime_handler(x):
        if isinstance(x, datetime.datetime):
            return x.isoformat()
        else:
            return x.__dict__

    tweets = []
    max_tweet = 10000

    try:
        collection_tweet_user.find_one_and_update(
            {"account_name": account_name}, {"$set": {"user_name": account_name}}, upsert=True
        )
    except Exception as e:
        print(e.details)

    try:
        for i, tweet in enumerate(
            snstwitter.TwitterUserScraper(username=account_name).get_items()
        ):
            if i > max_tweet:
                break
            tweet = json.dumps(tweet.__dict__, default=datetime_handler)
            tweets.append(json.loads(tweet))
    except Exception as e:
        print("error", e)

    try:
        collection_name.insert_many(tweets, bypass_document_validation=True)
    except BulkWriteError as e:
        print("error", e)


@celery_app.task()
def get_all_token():
    limit = 5000
    start = 1
    data = []
    while True:
        res = cmc.cryptocurrency_map(start=start, limit=limit)
        data = data + res.data
        start += limit
        if len(res.data) == 0:
            break
    try:
        collection_token.insert_many(data, bypass_document_validation=True)
    except BulkWriteError as e:
        print("error", e)


@celery_app.task()
def map_token_info(index_str: str):
    data = []
    res = cmc.cryptocurrency_info(id=index_str)
    for key, value in res.data.items():
        data.append(value)
    try:
        for d in data:
            token_id = d["id"]
            collection_token.find_one_and_update(
                {"id": token_id}, {"$set": d}, upsert=True
            )
    except BulkWriteError as e:
        print("error", e)


@task_success.connect(sender=extract_twitter_tweet)
def task_success_handler(sender, result, **kwargs):
    record = {"task_id": sender.request.id, "account_name": sender.request.args[0],
              "created_at": datetime.datetime.now()}
    print(
        "task_success_handler",
        record
    )
    collection_celery_task.insert_one(
        record
    )


@celery_app.task()
def update_extract_twitter_tweet():
    users = collection_tweet_user.find()
    for user in users:
        account_name = user.get('account_name')
        extract_twitter_tweet.delay(account_name)
