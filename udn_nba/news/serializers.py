from rest_framework import serializers

from .models import Author, NewsSession


class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for authors."""

    class Meta:
        model = Author
        fields = ["id", "name"]


class NewsSessionSerializer(serializers.ModelSerializer):
    """Serializer for news session."""

    news_count = serializers.SerializerMethodField()

    class Meta:
        model = NewsSession
        fields = ["id", "created_at", "news_count"]

    def get_news_count(self, obj) -> int:
        return obj.news.count()
