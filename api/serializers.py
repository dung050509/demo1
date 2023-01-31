from django.contrib.auth import get_tweet_model
from rest_framework import serializers

Tweet = get_tweet_model


class TeacrawlerSerializers(serializers.ModelSerializer):
    class Meta :
        model = Tweet
        field = ["id", "hashtags"]



# from rest_framework import serializers


# class TwitterUserSerializer(serializers.Serializer):
#     account_name = serializers.CharField(max_length=255)

#     def create(self, validated_data):
#         print(validated_data)
#         pass
    


