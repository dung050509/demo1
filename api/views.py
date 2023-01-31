import csv
import io
import os
import bson
import pymongo
import requests
import tweepy
import json
import time

from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.conf import settings

from teatwitter.teacrawler.tasks import extract_twitter_tweet, collection_tweet_user
from celery.result import AsyncResult
from django.http import JsonResponse
from teatwitter.utils.storages import MediaStorage
from datetime import datetime, timedelta

from django.shortcuts import render
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import TwitterUserSerializer

bearer_token = settings.TWITTER_BEARER
twitter_client = tweepy.Client(bearer_token)
twitter_auth = tweepy.OAuth2BearerHandler(bearer_token)
twitter_api_v1 = tweepy.API(twitter_auth)
my_client = pymongo.MongoClient(settings.DB_NAME)

dbname = my_client['twittertool']
collection_name = dbname['tweet']
chart_collection = dbname['chart']
collection_token = dbname['token']
collection_celery_task = dbname["celery_task"]
collection_tweet_user = dbname["tweet_user"]


@api_view(['GET'])
@permission_classes([AllowAny])
def search_user_view(request):
    """
    List all code snippets, or create a new snippet.
    """

    def gen_query(_account_name, _created_at):
        _queries = []
        if _account_name:
            _queries.append({'$text': {'$search': _account_name}})
        if _created_at:
            _queries.append({'created_at': {'$gte': _created_at}})
        _queries.append({'inReplyToTweetId': None})
        return _queries

    if request.method == 'GET':
        account_name = request.GET.get('account_name')
        kwargs = {'user_fields': ['description', 'entities', 'id', 'location', 'name', 'pinned_tweet_id',
                                  'profile_image_url', 'protected', 'public_metrics', 'url', 'username', 'verified',
                                  'withheld']}
        tasks = []
        users = []
        try:
            res = twitter_client.get_users(usernames=account_name.split(','), **kwargs)
            # get time before 30 minutes
            created_at = datetime.now() - timedelta(minutes=30)
            if len(res) > 0:
                for user in res.data:
                    queries = gen_query(user.username, created_at)
                    exited_data = collection_celery_task.find_one({'$and': queries})
                    if exited_data:
                        tasks.append(exited_data['task_id'])
                    else:
                        task = extract_twitter_tweet.delay(user.username)
                        tasks.append(task.id)
                    user_dict = user.data
                    users.append(user_dict)
            data = {
                'users': users,
                'tasks': tasks
            }
            return Response(data)
        except Exception as e:
            print(e)
            return Response(e)


@api_view(['GET'])
@permission_classes([AllowAny])
def search_user_tweet(request):
    """
    List all code snippets, or create a new snippet.
    """

    def gen_query(_account_ids, _keywords, _start_date, _end_date):
        _queries = []
        if _account_ids:
            ids = [bson.Int64(account_id) for account_id in _account_ids.split(',')]
            _queries.append({'user.id': {'$in': ids}})
        if _keywords:
            _queries.append({'$text': {'$search': keywords}})
        if start_date and end_date:
            _queries.append({'date': {'$gte': start_date, '$lte': end_date}})
        _queries.append({'inReplyToTweetId': None})
        return _queries

    if request.method == 'GET':
        data = []
        account_ids = request.GET.get('account_ids')
        keywords = request.GET.get('keywords')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        queries = gen_query(account_ids, keywords, start_date, end_date)
        res = collection_name.find({'$and': queries})
        for r in res:
            del r['_id']
            data.append(r)
        return Response({'data': data, 'count': len(data)})


@api_view(['GET'])
@permission_classes([AllowAny])
def get_task_process(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        data = {}
        task_ids = request.GET.get('task_ids').split(',')
        for task_id in task_ids:
            existed_task = collection_celery_task.find_one({'task_id': task_id})
            if existed_task:
                data[task_id] = 'SUCCESS'
            else:
                res = AsyncResult(id=task_id)
                data[f'{task_id}'] = res.state
        return Response(data)


@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def save_chart(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'POST':
        data = request.body
        res = chart_collection.insert_one(json.loads(data))
        return Response({"chart_id": str(res.inserted_id)})

    if request.method == 'GET':
        data = request.GET.get('chart_id')
        res = chart_collection.find_one({'_id': bson.ObjectId(data)})
        del res['_id']
        return Response(res)


@api_view(['POST'])
@permission_classes([AllowAny])
def upload_image(request):
    """
    A function to upload image to aws s3 storage
    """
    if request.method == 'POST':
        file_obj = request.FILES.get('file', '')
        wraped = request.POST.get('wraped', '')
        wraped = True if wraped == 'true' else False

        now = time.time()

        # do your validation here e.g. file size/type check

        # organize a path for the file in bucket
        file_directory_within_bucket = 'twittertool'

        # synthesize a full file path; note that we included the filename
        if wraped:
            file_path_within_bucket = f'{file_directory_within_bucket}/{file_obj.name}'
        else:
            file_path_within_bucket = os.path.join(
                file_directory_within_bucket,
                f'{int(now)}_{file_obj.name}'
            )

        media_storage = MediaStorage()

        if not media_storage.exists(file_path_within_bucket) or wraped:  # avoid overwriting existing file
            media_storage.save(file_path_within_bucket, file_obj)
            file_url = media_storage.url(file_path_within_bucket)

            return JsonResponse({
                'message': 'OK',
                'fileUrl': file_url,
            })
        else:
            return JsonResponse({
                'message': 'Error: file {filename} already exists at {file_directory} in bucket {bucket_name}'.format(
                    filename=file_obj.name,
                    file_directory=file_directory_within_bucket,
                    bucket_name=media_storage.bucket_name
                ),
            }, status=400)


@api_view(['GET'])
@permission_classes([AllowAny])
@cache_page(settings.CACHE_TTL)
def search_cmc_token(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        data = []
        keyword = request.GET.get('keyword')
        if keyword:
            res = collection_token.find({'symbol': {'$regex': keyword.upper()}})
        else:
            res = collection_token.find()
        for r in res:
            data.append(
                {
                    'id': r['id'],
                    'name': r['name'],
                    'symbol': r['symbol'],
                    'first_historical_data': r['first_historical_data'],
                    'logo': r['logo'] if 'logo' in r else '',
                }
            )
        return Response({'data': data, 'count': len(data)})


@api_view(['GET'])
@permission_classes([AllowAny])
def search_token_detail(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        time_start = request.GET.get('time_start', "2022-01-01")
        time_end = request.GET.get('time_end', datetime.today().strftime("%Y-%m-%d"))
        token_id = request.GET.get('token_id')
        interval = request.GET.get('interval')

        response = requests.get(
            url="https://web-api.coinmarketcap.com/v1.1/cryptocurrency/quotes/historical",
            params={
                "convert": "USD",
                "format": "chart_crypto_details",
                "interval": f"{interval}",
                "id": token_id,
                "time_start": time_start,
                "time_end": time_end
            }
        )
        return Response(json.loads(response.text))


@api_view(['GET'])
@permission_classes([AllowAny])
def get_detail_tweet(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        tweet_url = request.GET.get('tweet_url')
        tweet_id = tweet_url.split('/')[-1]
        try:
            user_fields = ["created_at", "description", "id", "location", "name", "profile_image_url", "protected",
                           "public_metrics", "url", "username", "verified", "withheld"]
            tweet_fields = ["created_at", "public_metrics", "referenced_tweets", "reply_settings", "source", "text"]
            res = twitter_client.get_tweet(id=tweet_id, user_fields=user_fields, tweet_fields=tweet_fields,
                                           expansions="author_id")
            user = res.includes.get('users')[0]
            res_user = {
                "id": user.get("id"),
                "displayname": user.get("name"),
                "username": user.get("username"),
                "profileImageUrl": user.get("profile_image_url"),
            }
            data = {
                "id": res.data.id,
                "date": str(res.data.created_at),
                "content": res.data.text,
                "replyCount": res.data.public_metrics.get("reply_count"),
                "likeCount": res.data.public_metrics.get("like_count"),
                "retweetCount": res.data.public_metrics.get("retweet_count"),
                "quoteCount": res.data.public_metrics.get("quote_count"),
                "url": tweet_url,
                "link": res.data.text,
                "user": res_user
            }
            return Response(data)
        except Exception as e:
            print(e)
            return Response(e)


@api_view(['GET'])
@permission_classes([AllowAny])
def live_search_user_view(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        account_name = request.GET.get('account_name')
        page = request.GET.get('page', 0)
        data = []
        try:
            users = twitter_api_v1.search_users(q=account_name, count=20, page=page)
            if users:
                for user in users:
                    data.append(
                        {
                            "name": user.name,
                            "username": user.screen_name,
                            "profile_image_url": user.profile_image_url_https,
                            "id": f"{user.id}"
                        }
                    )
            return Response(data)
        except Exception as e:
            print(e)
            return Response(e)


class TwitterUserImportView(APIView):
    permission_classes([AllowAny])

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file', '')
        file_obj_extension = file_obj.name.split('.')[-1]
        if file_obj_extension not in ['csv']:
            return Response("File extension not supported", status=400)

        # read csv file
        csv_file = file_obj.read().decode('utf-8')
        io_string = io.StringIO(csv_file)
        next(io_string)
        data = []
        for column in csv.reader(io_string, delimiter=',', quotechar="|"):
            account_name = column[0]
            print(account_name)
            data.append(
                {
                    "account_name": account_name,
                    "user_name": account_name,
                }
            )
        try:
            collection_tweet_user.insert_many(data, bypass_document_validation=True)
        except Exception as e:
            print(e.details)
        return Response(status=200)
