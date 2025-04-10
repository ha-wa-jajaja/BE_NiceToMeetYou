import unittest
from unittest.mock import MagicMock, patch

from django.db.utils import DatabaseError
from django.test import TestCase
from news.models import Author
from news.scrape import (
    UdnNbaParsers,  # Update this import path to match your project structure
)
from tags.models import Tag


class TestUdnNbaParsers(TestCase):
    """Test cases for UdnNbaParsers class."""

    def setUp(self):
        """Set up test environment."""
        self.parser = UdnNbaParsers()

        # Create test tags
        self.tag1 = Tag.objects.create(name="NBA")
        self.tag2 = Tag.objects.create(name="Lakers")
        self.tag3 = Tag.objects.create(name="Warriors")

    def test_title_parser_matching_tags(self):
        """Test title_parser returns correct tags when matches are found."""
        title = "NBA: Lakers defeat Warriors in overtime"

        matching_tags = self.parser.title_parser(title)

        # Check that all three tags are returned
        self.assertEqual(len(matching_tags), 3)
        self.assertIn(self.tag1, matching_tags)
        self.assertIn(self.tag2, matching_tags)
        self.assertIn(self.tag3, matching_tags)

    def test_title_parser_no_matching_tags(self):
        """Test title_parser returns empty list when no matches are found."""
        title = "Baseball: Yankees win World Series"

        matching_tags = self.parser.title_parser(title)

        # Check that no tags are returned
        self.assertEqual(len(matching_tags), 0)
        self.assertEqual(matching_tags, [])

    def test_title_parser_partial_match(self):
        """Test title_parser with partial matches."""
        title = "NBA highlights: Best plays of the week"

        matching_tags = self.parser.title_parser(title)

        # Check that only NBA tag is returned
        self.assertEqual(len(matching_tags), 1)
        self.assertIn(self.tag1, matching_tags)

    @patch("tags.models.Tag.objects")
    def test_title_parser_exception_handling(self, mock_tag_objects):
        """Test title_parser handles exceptions and returns empty list."""
        # Set up the mock to raise an exception
        mock_tag_objects.all.side_effect = Exception("Database connection error")

        title = "NBA: Lakers win championship"

        # Call the method and check that it returns an empty list
        result = self.parser.title_parser(title)
        self.assertEqual(result, [])

        # Verify that the exception was logged
        # Note: You might need to mock the logger and assert it was called correctly

    def test_author_parser_existing_author(self):
        """Test author_parser returns existing author."""
        # Create an author first
        existing_author = Author.objects.create(name="John Doe")

        author = self.parser.author_parser("John Doe")

        # Check that the correct author is returned
        self.assertEqual(author, existing_author)

        # Check that no new author was created
        self.assertEqual(Author.objects.count(), 1)

    def test_author_parser_new_author(self):
        """Test author_parser creates and returns new author when not existing."""
        author_name = "Jane Smith"

        # Verify author doesn't exist yet
        self.assertEqual(Author.objects.filter(name=author_name).count(), 0)

        author = self.parser.author_parser(author_name)

        # Check that a new author was created and returned
        self.assertIsNotNone(author)
        self.assertEqual(author.name, author_name)
        self.assertEqual(Author.objects.count(), 1)

    @patch("news.models.Author.objects")
    def test_author_parser_exception_handling(self, mock_author_objects):
        """Test author_parser handles exceptions and returns None."""
        # Set up the mock to raise an exception
        mock_author_objects.get_or_create.side_effect = DatabaseError(
            "Database connection error"
        )

        author_name = "Error Author"

        # Call the method and check that it returns None
        result = self.parser.author_parser(author_name)
        self.assertIsNone(result)

        # Verify that the exception was logged
        # Note: You might need to mock the logger and assert it was called correctly


if __name__ == "__main__":
    unittest.main()
