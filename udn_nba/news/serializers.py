from rest_framework import serializers
from tags.serializers import TagSerializer

from .models import Author, News, NewsSession


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


class NewsSerializer(serializers.ModelSerializer):
    """Serializer for news."""

    class Meta:
        model = News
        fields = [
            "id",
            "title",
            "thumbnail_url",
            "created_at",
        ]


class NewsDetailSerializer(NewsSerializer):
    """Serializer for news detail."""

    author = AuthorSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    session = NewsSessionSerializer(read_only=True)

    class Meta(NewsSerializer.Meta):
        fields = NewsSerializer.Meta.fields + [
            "author",
            "content",
            "session",
            "tags",
            "original_url",
        ]
