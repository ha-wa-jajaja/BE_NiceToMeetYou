import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from news.models import Author, News, NewsSession
from rest_framework import status
from rest_framework.test import APIClient


class NewsSessionViewSetTests(TestCase):
    """Test suite for the NewsSession API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Create an author for our news articles
        self.author = Author.objects.create(name="Test Author")

        # Create test sessions with specific dates
        # We'll manually set created_at for testing date filters

        # Session from 2022-01-15
        self.session_2022_jan = NewsSession.objects.create()
        # Update the created_at field directly in the database
        NewsSession.objects.filter(pk=self.session_2022_jan.pk).update(
            created_at=datetime.datetime(2022, 1, 15, 12, 0, tzinfo=timezone.utc)
        )
        # Refresh from db to get the updated value
        self.session_2022_jan.refresh_from_db()

        # Session from 2022-02-20
        self.session_2022_feb = NewsSession.objects.create()
        NewsSession.objects.filter(pk=self.session_2022_feb.pk).update(
            created_at=datetime.datetime(2022, 2, 20, 12, 0, tzinfo=timezone.utc)
        )
        self.session_2022_feb.refresh_from_db()

        # Session from 2023-02-20
        self.session_2023_feb = NewsSession.objects.create()
        NewsSession.objects.filter(pk=self.session_2023_feb.pk).update(
            created_at=datetime.datetime(2023, 2, 20, 12, 0, tzinfo=timezone.utc)
        )
        self.session_2023_feb.refresh_from_db()

        # Add some news to each session
        News.objects.create(
            title="News 1",
            content="Content 1",
            original_url="http://example.com/1",
            thumbnail_url="http://example.com/thumb1.jpg",
            author=self.author,
            session=self.session_2022_jan,
        )

        News.objects.create(
            title="News 2",
            content="Content 2",
            original_url="http://example.com/2",
            thumbnail_url="http://example.com/thumb2.jpg",
            author=self.author,
            session=self.session_2022_jan,
        )

        News.objects.create(
            title="News 3",
            content="Content 3",
            original_url="http://example.com/3",
            thumbnail_url="http://example.com/thumb3.jpg",
            author=self.author,
            session=self.session_2022_feb,
        )

        News.objects.create(
            title="News 4",
            content="Content 4",
            original_url="http://example.com/4",
            thumbnail_url="http://example.com/thumb4.jpg",
            author=self.author,
            session=self.session_2023_feb,
        )

    def test_list_sessions(self):
        """Test retrieving a list of news sessions."""
        url = reverse("news:newssession-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # We created 3 sessions in setUp

        # Verify the news_count in the response
        for session in response.data:
            if session["id"] == self.session_2022_jan.id:
                self.assertEqual(session["news_count"], 2)
            elif session["id"] in [self.session_2022_feb.id, self.session_2023_feb.id]:
                self.assertEqual(session["news_count"], 1)

    def test_retrieve_session(self):
        """Test retrieving a single news session."""
        url = reverse("news:newssession-detail", args=[self.session_2022_jan.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.session_2022_jan.id)
        self.assertEqual(response.data["news_count"], 2)

    def test_filter_sessions_by_year(self):
        """Test filtering sessions by year."""
        url = reverse("news:newssession-list")

        # Filter for 2022
        response = self.client.get(f"{url}?year=2022")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data), 2
        )  # Should return both Jan and Feb 2022 sessions

        # Filter for 2023
        response = self.client.get(f"{url}?year=2023")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Should return only Feb 2023 session

        # Filter for a year with no sessions
        response = self.client.get(f"{url}?year=2021")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # Should return empty list

    def test_filter_sessions_by_month(self):
        """Test filtering sessions by year and month."""
        url = reverse("news:newssession-list")

        # Filter for January 2022
        response = self.client.get(f"{url}?year=2022&month=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only the January 2022 session
        self.assertEqual(response.data[0]["id"], self.session_2022_jan.id)

        # Filter for February 2022
        response = self.client.get(f"{url}?year=2022&month=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only the February 2022 session
        self.assertEqual(response.data[0]["id"], self.session_2022_feb.id)

        # Filter for a month with no sessions
        response = self.client.get(f"{url}?year=2022&month=3")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # Should return empty list

    def test_filter_sessions_by_day(self):
        """Test filtering sessions by year, month, and day."""
        url = reverse("news:newssession-list")

        # Filter for January 15, 2022
        response = self.client.get(f"{url}?year=2022&month=1&day=15")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data), 1
        )  # Should find the January 15, 2022 session
        self.assertEqual(response.data[0]["id"], self.session_2022_jan.id)

        # Filter for January 16, 2022 (no sessions on this day)
        response = self.client.get(f"{url}?year=2022&month=1&day=16")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # Should return empty list

    def test_filter_validation_month_without_year(self):
        """Test that filtering by month without year raises an error."""
        url = reverse("news:newssession-list")

        response = self.client.get(f"{url}?month=1")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_validation_day_without_year_month(self):
        """Test that filtering by day without year and month raises an error."""
        url = reverse("news:newssession-list")

        # Test day without year or month
        response = self.client.get(f"{url}?day=15")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test day with year but without month
        response = self.client.get(f"{url}?year=2022&day=15")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
