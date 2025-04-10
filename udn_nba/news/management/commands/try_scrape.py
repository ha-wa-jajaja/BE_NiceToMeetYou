# tags/management/commands/load_tags.py
import json
import os

from django.core.management.base import BaseCommand
from news.models import News, NewsSession
from news.scrape.parsers import UdnNbaParsers
from news.scrape.scrapers import UdnNbaScraper


class Command(BaseCommand):
    help = "Test Scraping"

    def handle(self, *args, **options):
        # Create an instance of the scraper
        scraper = UdnNbaScraper()
        # parser = UdnNbaParsers()

        # Call the instance method
        new_featured_news = scraper.get_homepage_featured_news_urls()

        if not new_featured_news or not len(new_featured_news):
            self.stdout.write(self.style.WARNING("No new news"))
            return

        self.stdout.write(
            self.style.SUCCESS(f"Found {len(new_featured_news)} featured news items")
        )

        # news_session = NewsSession.objects.create()

        # TODO: Make news fetching asynchronous
        for url in new_featured_news:
            news_detail = scraper.get_news_detail(url)

            if not news_detail:
                self.stdout.write(
                    self.style.WARNING(f"Failed to retrieve news detail for {url}")
                )
                continue

            # TODO: Update these to objects after scraper update
            # tag_ids = parser.title_parser(news_detail["title"])
            # author_id = (
            #     parser.author_parser(news_detail["author"])
            #     if news_detail["author"]
            #     else None
            # )

            # TODO: Create news instance

            # TODO: On finish, websocket message?
            # if news_detail:
            #     self.stdout.write(
            #         self.style.SUCCESS("Successfully retrieved news details:")
            #     )
            #     self.stdout.write(f"Title: {news_detail['title']}")
            #     self.stdout.write(f"Author: {news_detail['author'] or 'Not available'}")
            #     self.stdout.write(f"Thumbnail: {news_detail['thumbnail']}")
