from django.core.management.base import BaseCommand
from django.db import transaction
from news.models import News, NewsSession
from news.scrape.parsers import UdnNbaParsers
from news.scrape.scrapers import UdnNbaScraper


class Command(BaseCommand):
    help = "Test Scraping"

    def handle(self, *args, **options):
        scraper = UdnNbaScraper()
        parser = UdnNbaParsers()

        # Call the instance method
        new_featured_news = scraper.get_homepage_featured_news_urls()

        if not new_featured_news or not len(new_featured_news):
            self.stdout.write(self.style.WARNING("No new news"))
            return

        self.stdout.write(
            self.style.SUCCESS(f"Found {len(new_featured_news)} featured news items")
        )

        with transaction.atomic():

            news_session = NewsSession.objects.create()

            # TODO: Make news fetching asynchronous
            for url in new_featured_news:
                news_detail = scraper.get_news_detail(url)

                if not news_detail:
                    self.stdout.write(
                        self.style.WARNING(f"Failed to retrieve news detail for {url}")
                    )
                    continue

                tags = parser.title_parser(news_detail["title"])
                author = (
                    parser.author_parser(news_detail["author"])
                    if news_detail["author"]
                    else None
                )

                # Create news instance
                news = News.objects.create(
                    title=news_detail["title"],
                    content=news_detail["content"],
                    original_url=url,
                    thumbnail_url=news_detail["thumbnail"],
                    author=author,
                    session=news_session,
                )

                # Add tags to the news
                if tags:
                    news.tags.add(*tags)

                # TODO: On finish, websocket message?
