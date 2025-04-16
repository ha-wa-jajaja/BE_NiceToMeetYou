import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from news.models import Author, News, NewsSession
from rest_framework import status
from rest_framework.test import APIClient
from tags.models import Tag


class NewsViewSetTests(TestCase):
    """Test suite for the News API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Create test author
        self.author = Author.objects.create(name="Test Author")

        # Create test tags
        self.tag1 = Tag.objects.create(name="NBA", type="League")
        self.tag2 = Tag.objects.create(name="Lakers", type="Teams")

        # Create test session
        self.news_session = NewsSession.objects.create()

        # Create test news with specific dates for ordering tests
        # News 1 - Oldest
        self.news1 = News.objects.create(
            title="Oldest News",
            content="Content for oldest news",
            original_url="http://example.com/oldest",
            thumbnail_url="http://example.com/thumb1.jpg",
            author=self.author,
            session=self.news_session,
        )
        # Manually update created_at to be 2 days ago
        News.objects.filter(pk=self.news1.pk).update(
            created_at=timezone.now() - datetime.timedelta(days=2)
        )
        self.news1.refresh_from_db()
        self.news1.tags.add(self.tag1)

        # News 2 - Middle
        self.news2 = News.objects.create(
            title="NBA Middle News",
            content="Content for middle news",
            original_url="http://example.com/middle",
            thumbnail_url="http://example.com/thumb2.jpg",
            author=self.author,
            session=self.news_session,
        )
        # Manually update created_at to be 1 day ago
        News.objects.filter(pk=self.news2.pk).update(
            created_at=timezone.now() - datetime.timedelta(days=1)
        )
        self.news2.refresh_from_db()
        self.news2.tags.add(self.tag1, self.tag2)

        # News 3 - Newest
        self.news3 = News.objects.create(
            title="Lakers Newest News",
            content="Content for newest news",
            original_url="http://example.com/newest",
            thumbnail_url="http://example.com/thumb3.jpg",
            author=self.author,
            session=self.news_session,
        )
        self.news3.tags.add(self.tag2)

        # Create additional news articles for pagination testing
        for i in range(4, 15):
            News.objects.create(
                title=f"News {i}",
                content=f"Content {i}",
                original_url=f"http://example.com/news{i}",
                thumbnail_url=f"http://example.com/thumb{i}.jpg",
                author=self.author,
                session=self.news_session,
            )

    def test_list_news(self):
        """Test retrieving a list of news articles."""
        url = reverse("news:news-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check pagination is working
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)

        # Verify we get the default page size (12)
        self.assertEqual(len(response.data["results"]), 12)

        # Verify the count is correct (we created 14 news articles)
        self.assertEqual(response.data["count"], 14)

        # Check that we're using the list serializer (not including content field)
        for news_item in response.data["results"]:
            self.assertIn("id", news_item)
            self.assertIn("title", news_item)
            self.assertIn("thumbnail_url", news_item)
            self.assertIn("created_at", news_item)
            self.assertNotIn("content", news_item)
            self.assertNotIn("author", news_item)
            self.assertNotIn("tags", news_item)

    def test_retrieve_news(self):
        """Test retrieving a single news article."""
        url = reverse("news:news-detail", args=[self.news1.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that we're using the detail serializer
        self.assertEqual(response.data["id"], self.news1.id)
        self.assertEqual(response.data["title"], self.news1.title)
        self.assertEqual(response.data["content"], self.news1.content)
        self.assertEqual(response.data["original_url"], self.news1.original_url)
        self.assertEqual(response.data["thumbnail_url"], self.news1.thumbnail_url)

        # Check related objects
        self.assertEqual(response.data["author"]["id"], self.author.id)
        self.assertEqual(response.data["author"]["name"], self.author.name)
        self.assertEqual(response.data["session"]["id"], self.news_session.id)

        # Check tags
        self.assertEqual(len(response.data["tags"]), 1)
        self.assertEqual(response.data["tags"][0]["id"], self.tag1.id)
        self.assertEqual(response.data["tags"][0]["name"], self.tag1.name)

    def test_filter_by_tag(self):
        """Test filtering news by tag."""
        url = reverse("news:news-list")

        # Filter by NBA tag
        response = self.client.get(f"{url}?tags={self.tag1.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)  # Should match news1 and news2

        # Get the titles from the response
        result_titles = [item["title"] for item in response.data["results"]]

        # The default ordering is -created_at, so news2 should be first
        self.assertIn(self.news2.title, result_titles)
        self.assertIn(self.news1.title, result_titles)
        self.assertNotIn(self.news3.title, result_titles)

        # Filter by Lakers tag
        response = self.client.get(f"{url}?tags={self.tag2.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)  # Should match news2 and news3

        # Get the titles from the response
        result_titles = [item["title"] for item in response.data["results"]]

        self.assertIn(self.news3.title, result_titles)
        self.assertIn(self.news2.title, result_titles)
        self.assertNotIn(self.news1.title, result_titles)

    def test_filter_by_author(self):
        """Test filtering news by author."""
        url = reverse("news:news-list")

        # Filter by author
        response = self.client.get(f"{url}?author={self.author.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 14)  # All news have the same author

    def test_filter_by_session(self):
        """Test filtering news by session."""
        url = reverse("news:news-list")

        # Filter by session
        response = self.client.get(f"{url}?session={self.news_session.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 14)  # All news have the same session

    def test_search_by_title(self):
        """Test searching news by title."""
        url = reverse("news:news-list")

        # Search for 'NBA'
        response = self.client.get(f"{url}?search=NBA")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)  # Should match only news2
        self.assertEqual(response.data["results"][0]["title"], self.news2.title)

        # Search for 'Lakers'
        response = self.client.get(f"{url}?search=Lakers")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)  # Should match only news3
        self.assertEqual(response.data["results"][0]["title"], self.news3.title)

        # Search for 'News' (should match multiple)
        response = self.client.get(f"{url}?search=News")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["count"] > 1)  # Should match multiple news

    def test_ordering(self):
        """Test ordering news."""
        # Create a new isolated session for this test to ensure we only get our test articles
        test_session = NewsSession.objects.create()

        # Create three news articles with specific dates within our isolated session
        # News 1 - Oldest
        news1 = News.objects.create(
            title="Test Oldest News",
            content="Content for oldest test news",
            original_url="http://example.com/test_oldest",
            thumbnail_url="http://example.com/test_thumb1.jpg",
            author=self.author,
            session=test_session,
        )
        # Update created_at to 3 days ago
        News.objects.filter(pk=news1.pk).update(
            created_at=timezone.now() - datetime.timedelta(days=3)
        )
        news1.refresh_from_db()

        # News 2 - Middle
        news2 = News.objects.create(
            title="Test Middle News",
            content="Content for middle test news",
            original_url="http://example.com/test_middle",
            thumbnail_url="http://example.com/test_thumb2.jpg",
            author=self.author,
            session=test_session,
        )
        # Update created_at to 2 days ago
        News.objects.filter(pk=news2.pk).update(
            created_at=timezone.now() - datetime.timedelta(days=2)
        )
        news2.refresh_from_db()

        # News 3 - Newest
        news3 = News.objects.create(
            title="Test Newest News",
            content="Content for newest test news",
            original_url="http://example.com/test_newest",
            thumbnail_url="http://example.com/test_thumb3.jpg",
            author=self.author,
            session=test_session,
        )
        # Update created_at to 1 day ago
        News.objects.filter(pk=news3.pk).update(
            created_at=timezone.now() - datetime.timedelta(days=1)
        )
        news3.refresh_from_db()

        # Now test ordering using the session filter
        url = reverse("news:news-list")

        # Filter by our test session
        response = self.client.get(f"{url}?session={test_session.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Get the IDs from the results
        result_ids = [item["id"] for item in response.data["results"]]

        # Verify we only got our 3 test articles
        self.assertEqual(len(result_ids), 3, "Should have exactly 3 results")
        self.assertIn(news1.id, result_ids)
        self.assertIn(news2.id, result_ids)
        self.assertIn(news3.id, result_ids)

        # Default ordering is -created_at (newest first)
        # news3 should be first, then news2, then news1
        self.assertEqual(
            result_ids[0], news3.id, "news3 should be first with default ordering"
        )
        self.assertEqual(
            result_ids[1], news2.id, "news2 should be second with default ordering"
        )
        self.assertEqual(
            result_ids[2], news1.id, "news1 should be third with default ordering"
        )

        # Test explicit descending order
        response = self.client.get(
            f"{url}?session={test_session.id}&ordering=-created_at"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result_ids = [item["id"] for item in response.data["results"]]

        # Same order as default
        self.assertEqual(result_ids[0], news3.id)
        self.assertEqual(result_ids[1], news2.id)
        self.assertEqual(result_ids[2], news1.id)

        # Test ascending order
        response = self.client.get(
            f"{url}?session={test_session.id}&ordering=created_at"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result_ids = [item["id"] for item in response.data["results"]]

        # Should have news1 (oldest) first, then news2, then news3 (newest)
        self.assertEqual(
            result_ids[0], news1.id, "news1 should be first with ascending ordering"
        )
        self.assertEqual(
            result_ids[1], news2.id, "news2 should be second with ascending ordering"
        )
        self.assertEqual(
            result_ids[2], news3.id, "news3 should be third with ascending ordering"
        )

    def test_pagination(self):
        """Test news pagination."""
        url = reverse("news:news-list")

        # Default page size should be 12
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 12)
        self.assertIsNotNone(response.data["next"])  # Should have a next page
        self.assertIsNone(response.data["previous"])  # Should not have a previous page

        # Get the second page
        response = self.client.get(f"{url}?page=2")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data["results"]), 2
        )  # Should have 2 remaining items
        self.assertIsNone(response.data["next"])  # Should not have a next page
        self.assertIsNotNone(response.data["previous"])  # Should have a previous page

        # Test custom page size
        response = self.client.get(f"{url}?size=5")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 5)  # Should have 5 items
        self.assertIsNotNone(response.data["next"])  # Should have a next page

        # Test max page size
        response = self.client.get(f"{url}?size=100")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data["results"]), 14
        )  # Should have all 14 items, capped by max_page_size
