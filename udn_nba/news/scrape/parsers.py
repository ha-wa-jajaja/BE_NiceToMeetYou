from typing import List

from news.models import Author
from tags.models import Tag


class UdnNbaParsers:

    # This function is not realistic in a real-world scenario.
    # It is just a practice.
    def title_parser(self, title: str) -> List[int]:
        """
        Parse the title and return a list of tag IDs that match the title

        Args:
            title: The title of the news article

        Returns:
            List of tag IDs
        """
        # Get all tags
        all_tags = Tag.objects.all()

        # Find tags whose names are contained in the title
        matching_tag_ids = [tag.id for tag in all_tags if tag.name in title]

        return matching_tag_ids

    def author_parser(self, author_name: str) -> int:
        """
        Parse the author and return the author's ID
        Args:
            author_name: The name of the author
        Returns:
            The ID of the author
        """
        # Check if the author exists
        # Since we applied db_index on the name field, this should be fast
        author, created = Author.objects.get_or_create(name=author_name)

        return author.id
