from django.test import TestCase
from news.models import Author, News, NewsSession
from tags.models import Tag


class NewsTests(TestCase):
    def test_create_author(self):
        """Test creating a author is successful."""

        author = Author.objects.create(name="Test Author")

        self.assertEqual(str(author), author.name)

    def test_create_news_session(self):
        """Test creating a news session is successful."""

        session = NewsSession.objects.create()

        self.assertEqual(
            str(session),
            f"Session {session.id} ({session.created_at.strftime('%Y-%m-%d %H:%M')}) - {session.news.count()} articles",
        )

    def test_create_news(self):
        """Test creating a news is successful."""

        news = News.objects.create(
            title="Test Title",
            content="Test Content",
            thumbnail_url="https://example.com/image.jpg",
            author=Author.objects.create(name="Test Author"),
            session=NewsSession.objects.create(),
        )

        self.assertEqual(str(news), news.title)

        # Create tags
        team_tag = Tag.objects.create(name="Lakers", type="Teams")
        player_tag = Tag.objects.create(name="LeBron James", type="Players")

        # Add tags to the news article
        news.tags.add(team_tag)
        news.tags.add(player_tag)

        # Assert that the tags were added correctly
        self.assertEqual(news.tags.count(), 2)
        self.assertIn(team_tag, news.tags.all())
        self.assertIn(player_tag, news.tags.all())

        # Test reverse relationship (tags to news)
        self.assertIn(news, team_tag.news.all())
        self.assertIn(news, player_tag.news.all())
