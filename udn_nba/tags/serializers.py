from rest_framework import serializers
from tags.models import Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ["id", "name"]
        read_only_fields = ["id"]


class TagDetailSerializer(TagSerializer):
    """Serializer for recipe detail view."""

    class Meta(TagSerializer.Meta):
        fields = TagSerializer.Meta.fields + ["type"]
