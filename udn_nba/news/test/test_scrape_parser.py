from unittest.mock import MagicMock, patch

from django.test import TestCase
from news.scrape.parsers import UdnNbaParsers


class TestUdnNbaParsers(TestCase):
    """Test cases for UdnNbaParsers class"""

    def setUp(self):
        """Set up test fixtures"""
        self.parsers = UdnNbaParsers()

        # Create a mock logger for testing
        self.mock_logger = MagicMock()
        self.parsers.logger = self.mock_logger

    @patch("news.scrape.parsers.Tag.objects.all")
    def test_title_parser_with_matching_tags(self, mock_tags_all):
        """Test title_parser with matching tags in the title"""
        # Set up mock tag objects
        mock_tag1 = MagicMock()
        mock_tag1.id = 1
        mock_tag1.name = "Lakers"

        mock_tag2 = MagicMock()
        mock_tag2.id = 2
        mock_tag2.name = "NBA"

        mock_tag3 = MagicMock()
        mock_tag3.id = 3
        mock_tag3.name = "Playoffs"

        # Configure the mock Tag.objects.all() to return our mock tags
        mock_tags_all.return_value = [mock_tag1, mock_tag2, mock_tag3]

        # Call the method with a title containing some of the tags
        result = self.parsers.title_parser("Lakers win NBA championship")

        # Verify that the correct tag IDs were returned
        self.assertEqual(result, [1, 2])

        # Verify that Tag.objects.all() was called once
        mock_tags_all.assert_called_once()

    @patch("news.scrape.parsers.Tag.objects.all")
    def test_title_parser_with_no_matching_tags(self, mock_tags_all):
        """Test title_parser with no matching tags in the title"""
        # Set up mock tag objects
        mock_tag1 = MagicMock()
        mock_tag1.id = 1
        mock_tag1.name = "Lakers"

        mock_tag2 = MagicMock()
        mock_tag2.id = 2
        mock_tag2.name = "NBA"

        # Configure the mock Tag.objects.all() to return our mock tags
        mock_tags_all.return_value = [mock_tag1, mock_tag2]

        # Call the method with a title not containing any of the tags
        result = self.parsers.title_parser("Exciting game yesterday")

        # Verify that an empty list was returned
        self.assertEqual(result, [])

        # Verify that Tag.objects.all() was called once
        mock_tags_all.assert_called_once()

    @patch("news.scrape.parsers.Tag.objects.all")
    def test_title_parser_error_handling(self, mock_tags_all):
        """Test error handling in title_parser"""
        # Configure the mock to raise an exception
        mock_tags_all.side_effect = Exception("Database error")

        # Call the method
        result = self.parsers.title_parser("Test title")

        # Verify that an empty list is returned on error
        self.assertEqual(result, [])

        # Verify that the error was logged
        self.mock_logger.error.assert_called_once()
        self.assertIn("Error parsing title", str(self.mock_logger.error.call_args))

    @patch("news.scrape.parsers.Author.objects.get_or_create")
    def test_author_parser_existing_author(self, mock_get_or_create):
        """Test author_parser with an existing author"""
        # Set up mock author
        mock_author = MagicMock()
        mock_author.id = 42

        # Configure get_or_create to return existing author and False for created
        mock_get_or_create.return_value = (mock_author, False)

        # Call the method
        result = self.parsers.author_parser("John Doe")

        # Verify that the correct author ID was returned
        self.assertEqual(result, 42)

        # Verify that Author.objects.get_or_create was called with the right parameters
        mock_get_or_create.assert_called_once_with(name="John Doe")

    @patch("news.scrape.parsers.Author.objects.get_or_create")
    def test_author_parser_new_author(self, mock_get_or_create):
        """Test author_parser with a new author"""
        # Set up mock author
        mock_author = MagicMock()
        mock_author.id = 99

        # Configure get_or_create to return new author and True for created
        mock_get_or_create.return_value = (mock_author, True)

        # Call the method
        result = self.parsers.author_parser("Jane Smith")

        # Verify that the correct author ID was returned
        self.assertEqual(result, 99)

        # Verify that Author.objects.get_or_create was called with the right parameters
        mock_get_or_create.assert_called_once_with(name="Jane Smith")

    @patch("news.scrape.parsers.Author.objects.get_or_create")
    def test_author_parser_error_handling(self, mock_get_or_create):
        """Test error handling in author_parser"""
        # Configure the mock to raise an exception
        mock_get_or_create.side_effect = Exception("Database error")

        # Call the method
        result = self.parsers.author_parser("Test Author")

        # Verify that None is returned on error
        self.assertIsNone(result)

        # Verify that the error was logged
        self.mock_logger.error.assert_called_once()
        self.assertIn("Error parsing author", str(self.mock_logger.error.call_args))
