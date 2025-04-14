"""
Tests for tags API.

Tags are categorized as either Teams or Players according to the model definition.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from tags.models import Tag
from tags.serializers import TagDetailSerializer, TagSerializer

TAGS_URL = reverse("tags:tags-list")


def detail_url(tag_id):
    """Create and return a tag detail URL."""
    return reverse("tags:tags-detail", args=[tag_id])


def create_tag(name="Test tag", tag_type="Teams"):
    """Create and return a sample tag."""
    return Tag.objects.create(name=name, type=tag_type)


class PublicTagsApiTests(TestCase):
    """Test the publicly available tags API."""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_tags(self):
        """Test retrieving a list of tags."""
        create_tag(name="Barcelona", tag_type="Teams")
        create_tag(name="Messi", tag_type="Players")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by("id")
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_tags_by_type(self):
        """Test filtering tags by type."""
        tag1 = create_tag(name="Real Madrid", tag_type="Teams")
        tag2 = create_tag(name="Manchester", tag_type="Teams")
        tag3 = create_tag(name="Ronaldo", tag_type="Players")

        params = {"type": "Teams"}
        res = self.client.get(TAGS_URL, params)

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)
        s3 = TagSerializer(tag3)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)

    def test_filter_tags_by_name(self):
        """Test filtering tags by name."""
        tag1 = create_tag(name="Bayern Munich", tag_type="Teams")
        tag2 = create_tag(name="Manchester United", tag_type="Teams")
        tag3 = create_tag(name="Manchester City", tag_type="Teams")
        tag4 = create_tag(name="Ronaldo", tag_type="Players")

        params = {"name": "manchester"}
        res = self.client.get(TAGS_URL, params)

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)
        s3 = TagSerializer(tag3)
        s4 = TagSerializer(tag4)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertIn(s3.data, res.data)
        self.assertNotIn(s4.data, res.data)

    def test_exclusive_filtering_validation_error(self):
        """Test that using both name and type filters raises a validation error."""
        create_tag(name="Real Madrid", tag_type="Teams")
        create_tag(name="Manchester", tag_type="Teams")
        create_tag(name="Ronaldo", tag_type="Players")

        # Both name and type filters provided
        params = {"name": "ma", "type": "Players"}
        res = self.client.get(TAGS_URL, params)

        # Should return a 400 Bad Request with a validation error
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", res.data)

    def test_retrieve_tag_detail(self):
        """Test retrieving a tag detail."""
        tag = create_tag(name="Liverpool", tag_type="Teams")

        url = detail_url(tag.id)
        res = self.client.get(url)

        serializer = TagDetailSerializer(tag)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tag_detail_has_type(self):
        """Test that tag detail includes the type field."""
        tag = create_tag(name="Mbappé", tag_type="Players")

        url = detail_url(tag.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("type", res.data)
        self.assertEqual(res.data["type"], tag.type)
