from django.test import TestCase
from django.urls import reverse
from news.models import Author
from rest_framework import status
from rest_framework.test import APIClient


class AuthorViewSetTests(TestCase):
    """Test suite for the Author API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        # Create some test authors
        self.author1 = Author.objects.create(name="Test Author 1")
        self.author2 = Author.objects.create(name="Test Author 2")

    def test_list_authors(self):
        """Test retrieving a list of authors."""
        url = reverse("news:author-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # We created 2 authors in setUp

        # Check that both authors are present in the response
        author_names = [author["name"] for author in response.data]
        self.assertIn(self.author1.name, author_names)
        self.assertIn(self.author2.name, author_names)

    def test_retrieve_author(self):
        """Test retrieving a single author."""
        url = reverse("news:author-detail", args=[self.author1.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.author1.name)
        self.assertEqual(response.data["id"], self.author1.id)
