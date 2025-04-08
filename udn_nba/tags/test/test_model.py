from django.core.exceptions import ValidationError
from django.db import transaction, utils
from django.test import TestCase
from tags.models import Tag


class TagTests(TestCase):
    def test_create_team_tag(self):
        """Test creating a tag is successful."""
        tag = Tag.objects.create(
            name="Test Tag",
            type=Tag.TypeChoices.TEAMS,
        )

        self.assertEqual(str(tag), tag.name)

    def test_create_player_tag(self):
        """Test creating a tag is successful."""
        tag = Tag.objects.create(
            name="Test Tag",
            type=Tag.TypeChoices.PLAYERS,
        )

        self.assertEqual(str(tag), tag.name)

    def test_tag_name_max_length(self):
        """Test tag with name exceeding max length raises error."""
        # Create a tag with a name that exceeds the max length (255 characters)
        long_name = "a" * 256

        tag = Tag(
            name=long_name,
            type=Tag.TypeChoices.TEAMS,
        )

        # Use Django's full_clean to simulate validation that would happen in forms
        with self.assertRaises(ValidationError):
            tag.full_clean()

    def test_invalid_tag_type(self):
        """Test creating a tag with invalid type raises error."""
        # Try to create a tag with an invalid type
        tag = Tag(
            name="Test Tag",
            type="InvalidType",  # Not in the TypeChoices
        )

        # This should raise a validation error
        with self.assertRaises(ValidationError):
            tag.full_clean()

    def test_tag_name_uniqueness_within_type(self):
        """Test that tag names must be unique within a type."""
        # Create first tag
        Tag.objects.create(
            name="Duplicate Tag",
            type=Tag.TypeChoices.TEAMS,
        )

        # Try to create another tag with the same name and type
        with self.assertRaises(utils.IntegrityError):
            # Create a separate transaction that can fail without affecting the test's transaction
            with transaction.atomic():
                Tag.objects.create(
                    name="Duplicate Tag",
                    type=Tag.TypeChoices.TEAMS,  # Same type
                )

        # Verify we can create a tag with the same name but different type
        Tag.objects.create(
            name="Duplicate Tag",
            type=Tag.TypeChoices.PLAYERS,  # Different type
        )

        # Verify we now have two tags
        self.assertEqual(Tag.objects.count(), 2)
