import unittest
from unittest.mock import MagicMock, patch

import requests
from bs4 import BeautifulSoup
from django.test import TestCase
from news.models import News
from news.scrape.scrapers import UdnNbaHomeScraper, UdnNbaNewsScraper, UdnNbaScraper


class UdnNbaHomeScraperTests(TestCase):
    def setUp(self):
        self.logger = MagicMock()
        self.scraper = UdnNbaHomeScraper(self.logger)

    def test_parse_soup_get_featured_news(self):
        # Create sample HTML content for testing
        html_content = """
        <div>
            <ul class="splide__list">
                <li id="slide01" class="splide__slide">
                    <a href="http://example.com/news/1">News 1</a>
                </li>
                <li id="slide02-clone" class="splide__slide">
                    <a href="http://example.com/news/2">News 2</a>
                </li>
                <li id="slide03" class="splide__slide">
                    <a href="http://example.com/news/3">News 3</a>
                </li>
            </ul>
        </div>
        """
        soup = BeautifulSoup(html_content, "lxml")

        # Case 1: No news exists yet
        with patch("news.models.News.objects.filter") as mock_filter:
            # Mock the queryset returned by filter()
            mock_values_list = mock_filter.return_value.values_list
            mock_values_list.return_value = []

            urls = self.scraper.parse_soup_get_featured_news(soup)

            # Verify the filter was called with the right arguments
            mock_filter.assert_called_once_with(
                original_url__in=[
                    "http://example.com/news/1",
                    "http://example.com/news/3",
                ]
            )

            # Check results
            self.assertEqual(
                len(urls), 2
            )  # Should only get 2 URLs (excluding the clone)
            self.assertIn("http://example.com/news/1", urls)
            self.assertIn("http://example.com/news/3", urls)

        # Case 2: Some news already exists
        with patch("news.models.News.objects.filter") as mock_filter:
            # Mock the queryset returned by filter()
            mock_values_list = mock_filter.return_value.values_list
            mock_values_list.return_value = ["http://example.com/news/1"]

            urls = self.scraper.parse_soup_get_featured_news(soup)

            # Check results
            self.assertEqual(
                len(urls), 1
            )  # Should only get 1 URL (excluding the clone and existing news)
            self.assertEqual(urls[0], "http://example.com/news/3")


class UdnNbaNewsScraperTests(TestCase):
    def setUp(self):
        self.logger = MagicMock()
        self.scraper = UdnNbaNewsScraper(self.logger)

    def test_get_title(self):
        # Test successful title extraction
        html = '<div class="story_art_title">Test Title</div>'
        soup = BeautifulSoup(html, "lxml")
        self.assertEqual(self.scraper.get_title(soup), "Test Title")

        # Test empty title
        html = '<div class="story_art_title"></div>'
        soup = BeautifulSoup(html, "lxml")
        self.assertIsNone(self.scraper.get_title(soup))

        # Test missing title element
        html = '<div class="other_class">No Title Here</div>'
        soup = BeautifulSoup(html, "lxml")
        self.assertIsNone(self.scraper.get_title(soup))

    def test_get_thumbnail(self):
        # Test successful thumbnail extraction
        html = '<div class="photo-story"><img src="http://example.com/image.jpg"></div>'
        soup = BeautifulSoup(html, "lxml")
        self.assertEqual(
            self.scraper.get_thumbnail(soup), "http://example.com/image.jpg"
        )

        # Test missing src attribute
        html = '<div class="photo-story"><img></div>'
        soup = BeautifulSoup(html, "lxml")
        self.assertIsNone(self.scraper.get_thumbnail(soup))

        # Test missing thumbnail element
        html = '<div class="other_class">No Thumbnail Here</div>'
        soup = BeautifulSoup(html, "lxml")
        self.assertIsNone(self.scraper.get_thumbnail(soup))

    def test_get_author(self):
        # Test successful author extraction
        html = '<div class="shareBar__info--author">記者John Doe／報導</div>'
        soup = BeautifulSoup(html, "lxml")
        self.assertEqual(self.scraper.get_author(soup), "John Doe")

        # Test author with different format
        html = '<div class="shareBar__info--author">記者Jane Smith／台北報導</div>'
        soup = BeautifulSoup(html, "lxml")
        self.assertEqual(self.scraper.get_author(soup), "Jane Smith")

        # Test missing author element
        html = '<div class="other_class">No Author Here</div>'
        soup = BeautifulSoup(html, "lxml")
        self.assertIsNone(self.scraper.get_author(soup))

    def test_get_content(self):
        # Test successful content extraction
        html = """
        <div id="story_body_content">
            <span>
                <p>Paragraph 1</p>
                <p><figure>Image</figure></p>
                <p>Paragraph 2</p>
                <p></p>
                <p>Paragraph 3</p>
            </span>
        </div>
        """
        soup = BeautifulSoup(html, "lxml")
        expected_content = "Paragraph 1\nParagraph 2\nParagraph 3"
        self.assertEqual(self.scraper.get_content(soup), expected_content)

        # Test missing content
        html = '<div id="other_id">No Content Here</div>'
        soup = BeautifulSoup(html, "lxml")
        self.assertIsNone(self.scraper.get_content(soup))


class UdnNbaScraperTests(TestCase):
    def setUp(self):
        self.scraper = UdnNbaScraper()

        # Mock the logger
        self.mock_logger = MagicMock()
        self.scraper.logger = self.mock_logger

        # Mock the session
        self.scraper.session = MagicMock()

        # Mock the sub-scrapers
        self.scraper.home_scraper = MagicMock()
        self.scraper.news_scraper = MagicMock()

    @patch("requests.Session")
    @patch("news.scrape.scrapers.get_logger")
    def test_init(self, mock_get_logger, mock_session):
        # Create a new instance to test the __init__ method
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        scraper = UdnNbaScraper()

        # Check if the session headers were updated
        mock_session_instance.headers.update.assert_called_once_with(
            UdnNbaScraper.HEADERS
        )

        # Check if the logger was initialized correctly
        mock_get_logger.assert_called_once_with("news_scraper.UdnNbaScraper")

        # Check if the sub-scrapers were initialized
        self.assertIsInstance(scraper.home_scraper, UdnNbaHomeScraper)
        self.assertIsInstance(scraper.news_scraper, UdnNbaNewsScraper)

    def test_fetch_page_success(self):
        # Mock successful response
        mock_response = MagicMock()
        mock_response.text = "HTML content"
        self.scraper.session.get.return_value = mock_response

        result = self.scraper.fetch_page("http://example.com")

        self.assertEqual(result, "HTML content")
        self.scraper.session.get.assert_called_once_with(
            "http://example.com", timeout=30
        )
        mock_response.raise_for_status.assert_called_once()

    def test_fetch_page_error(self):
        # Mock error response
        self.scraper.session.get.side_effect = requests.RequestException("Error")

        result = self.scraper.fetch_page("http://example.com")

        self.assertIsNone(result)
        self.scraper.logger.error.assert_called_once()

    @patch("news.scrape.scrapers.BeautifulSoup")
    def test_get_homepage_featured_news_urls_success(self, mock_bs):
        # Mock fetch_page to return some HTML
        self.scraper.fetch_page = MagicMock(return_value="HTML content")

        # Mock BeautifulSoup
        mock_soup = MagicMock()
        mock_bs.return_value = mock_soup

        # Mock home_scraper.parse_soup_get_featured_news
        expected_urls = ["http://example.com/news/1", "http://example.com/news/2"]
        self.scraper.home_scraper.parse_soup_get_featured_news.return_value = (
            expected_urls
        )

        result = self.scraper.get_homepage_featured_news_urls()

        self.assertEqual(result, expected_urls)
        self.scraper.fetch_page.assert_called_once_with(self.scraper.BASE_URL)
        mock_bs.assert_called_once_with("HTML content", "lxml")
        self.scraper.home_scraper.parse_soup_get_featured_news.assert_called_once_with(
            mock_soup
        )
        self.scraper.logger.info.assert_called_once_with(
            f"Found {len(expected_urls)} featured news URLs."
        )

    def test_get_homepage_featured_news_urls_fetch_error(self):
        # Mock fetch_page to return None (error)
        self.scraper.fetch_page = MagicMock(return_value=None)

        result = self.scraper.get_homepage_featured_news_urls()

        self.assertEqual(result, [])
        self.scraper.fetch_page.assert_called_once_with(self.scraper.BASE_URL)
        self.scraper.logger.error.assert_called_once()

    def test_get_homepage_featured_news_urls_no_urls(self):
        # Mock fetch_page to return some HTML
        self.scraper.fetch_page = MagicMock(return_value="HTML content")

        # Mock home_scraper.parse_soup_get_featured_news to return empty list
        self.scraper.home_scraper.parse_soup_get_featured_news.return_value = []

        result = self.scraper.get_homepage_featured_news_urls()

        self.assertEqual(result, [])
        self.scraper.logger.error.assert_called_once()

    @patch("news.scrape.scrapers.BeautifulSoup")
    def test_get_news_detail_success(self, mock_bs):
        # Mock fetch_page to return some HTML
        self.scraper.fetch_page = MagicMock(return_value="HTML content")

        # Mock BeautifulSoup
        mock_soup = MagicMock()
        mock_bs.return_value = mock_soup

        # Mock news_scraper methods
        self.scraper.news_scraper.get_title.return_value = "Test Title"
        self.scraper.news_scraper.get_thumbnail.return_value = (
            "http://example.com/image.jpg"
        )
        self.scraper.news_scraper.get_content.return_value = "Test content"
        self.scraper.news_scraper.get_author.return_value = "John Doe"

        expected_data = {
            "title": "Test Title",
            "thumbnail": "http://example.com/image.jpg",
            "author": "John Doe",
            "content": "Test content",
        }

        result = self.scraper.get_news_detail("http://example.com/news/1")

        self.assertEqual(result, expected_data)
        self.scraper.fetch_page.assert_called_once_with("http://example.com/news/1")
        mock_bs.assert_called_once_with("HTML content", "lxml")
        self.scraper.news_scraper.get_title.assert_called_once_with(mock_soup)
        self.scraper.news_scraper.get_thumbnail.assert_called_once_with(mock_soup)
        self.scraper.news_scraper.get_content.assert_called_once_with(mock_soup)
        self.scraper.news_scraper.get_author.assert_called_once_with(mock_soup)

    def test_get_news_detail_fetch_error(self):
        # Mock fetch_page to return None (error)
        self.scraper.fetch_page = MagicMock(return_value=None)

        result = self.scraper.get_news_detail("http://example.com/news/1")

        self.assertIsNone(result)
        self.scraper.fetch_page.assert_called_once_with("http://example.com/news/1")
        self.scraper.logger.error.assert_called_once()

    @patch("news.scrape.scrapers.BeautifulSoup")
    def test_get_news_detail_missing_required_fields(self, mock_bs):
        # Mock fetch_page to return some HTML
        self.scraper.fetch_page = MagicMock(return_value="HTML content")

        # Mock BeautifulSoup
        mock_soup = MagicMock()
        mock_bs.return_value = mock_soup

        # Mock news_scraper methods with missing thumbnail
        self.scraper.news_scraper.get_title.return_value = "Test Title"
        self.scraper.news_scraper.get_thumbnail.return_value = None  # Missing
        self.scraper.news_scraper.get_content.return_value = "Test content"

        result = self.scraper.get_news_detail("http://example.com/news/1")

        self.assertIsNone(result)
        self.scraper.logger.error.assert_called_once()

    @patch("news.scrape.scrapers.BeautifulSoup")
    def test_get_news_detail_unexpected_exception(self, mock_bs):
        # Mock fetch_page to return some HTML
        self.scraper.fetch_page = MagicMock(return_value="HTML content")

        # Mock BeautifulSoup to raise an exception
        mock_bs.side_effect = Exception("Unexpected error")

        result = self.scraper.get_news_detail("http://example.com/news/1")

        self.assertIsNone(result)
        self.scraper.logger.error.assert_called_once()


if __name__ == "__main__":
    unittest.main()
