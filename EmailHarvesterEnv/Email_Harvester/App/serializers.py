from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ScrapingHistory

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class ScrapingHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapingHistory
        fields = ['id', 'url', 'scraped_at', 'email_count']

class URLInputSerializer(serializers.Serializer):
    url = serializers.URLField()