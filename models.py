from django.db import models


# Create your models here.

class KOLMaster(models.Model):
    name = models.CharField(max_length=100)
    twitter_url = models.CharField(max_length=255)
    search_count = models.IntegerField(default=0)
    follower_count = models.IntegerField(default=0)
    description = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'kol_master'
        verbose_name = 'KOL Master'
        verbose_name_plural = 'KOL Master'


class Tweet(models.Model):
    tweet_id = models.BigIntegerField()
    content = models.TextField()
    conversation_id = models.BigIntegerField()
    date = models.DateTimeField()
    in_reply_to_tweet_id = models.BigIntegerField()
    in_reply_to_user_id = models.BigIntegerField()
    like_count = models.IntegerField()
    rendered_content = models.TextField()
    source = models.CharField(max_length=255)
    source_label = models.CharField(max_length=255)
    source_url = models.CharField(max_length=255)
    url = models.CharField(max_length=255)


class TwitterUser(models.Model):
    twitter_id = models.BigIntegerField()
    username = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    followers_count = models.IntegerField()
    friends_count = models.IntegerField()
    listed_count = models.IntegerField()
    favourites_count = models.IntegerField()
    statuses_count = models.IntegerField()
    created_at = models.DateTimeField()
    verified = models.BooleanField()
    profile_background_image_url = models.CharField(max_length=255)
    profile_background_banner_url = models.CharField(max_length=255)
    official = models.BooleanField()

    class Meta:
        db_table = 'twitter_user'
        verbose_name = 'Twitter User'
        verbose_name_plural = 'Twitter User'
