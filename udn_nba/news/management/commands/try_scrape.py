# tags/management/commands/load_tags.py
import json
import os

from django.core.management.base import BaseCommand
from news.scrape.parsers import UdnNbaParsers
from news.scrape.scrapers import UdnNbaScraper


class Command(BaseCommand):
    help = "Test Scraping"

    def handle(self, *args, **options):
        # Create an instance of the scraper
        scraper = UdnNbaScraper()

        # Call the instance method
        featured_news = scraper.get_homepage_featured_news_urls()

        if not featured_news:
            self.stdout.write(self.style.WARNING("No new news"))
            return

        self.stdout.write(
            self.style.SUCCESS(f"Found {len(featured_news)} featured news items")
        )
        for url in featured_news:
            news_detail = scraper.get_news_detail(url)

            if news_detail:
                self.stdout.write(
                    self.style.SUCCESS("Successfully retrieved news details:")
                )
                self.stdout.write(f"Title: {news_detail['title']}")
                self.stdout.write(f"Author: {news_detail['author'] or 'Not available'}")
                self.stdout.write(f"Thumbnail: {news_detail['thumbnail']}")
