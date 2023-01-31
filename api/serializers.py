from rest_framework import serializers


class TwitterUserSerializer(serializers.Serializer):
    account_name = serializers.CharField(max_length=255)

    def create(self, validated_data):
        print(validated_data)
        pass
