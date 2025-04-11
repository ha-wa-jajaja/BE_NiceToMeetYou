import logging
import re
from typing import List, Optional, TypedDict

import requests
from bs4 import BeautifulSoup
from news.models import News

from .logger import get_logger


class NewsData(TypedDict):
    title: str
    thumbnail: str
    author: str
    content: str


class UdnNbaScraper:
    BASE_URL = "https://tw-nba.udn.com/nba/index"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    def __init__(self):
        """Initialize scraper with default configuration"""
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self.logger = get_logger("news_scraper.UdnNbaScraper")

        self.home_scraper = UdnNbaHomeScraper(self.logger)
        self.news_scraper = UdnNbaNewsScraper(self.logger)

    def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch HTML content from the given URL

        Args:
            url: The URL to fetch

        Returns:
            HTML content or None if an error occurs
        """
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            self.logger.error(f"Error fetching {url}: {str(e)}")
            return None

    def get_homepage_featured_news_urls(self) -> List[str]:
        """
        Extract featured news from the homepage

        Returns:
            List of dictionaries containing news urls
        """
        html_content = self.fetch_page(self.BASE_URL)

        if not html_content:
            self.logger.error(f"Failed to fetch content from {self.BASE_URL}")
            return []

        soup = BeautifulSoup(html_content, "lxml")

        # Parse the soup to get featured news URLs
        featured_news_urls = self.home_scraper.parse_soup_get_featured_news(soup)

        if not featured_news_urls:
            self.logger.error("No featured news URLs found.")
            return []

        self.logger.info(f"Found {len(featured_news_urls)} featured news URLs.")

        return featured_news_urls

    def get_news_detail(self, url: str) -> Optional[NewsData]:
        """
        Process a news article data.

        Args:
            url: url of the news.

        Returns:
            A dictionary containing:
                - title: The original title or processed title
                - thumbnail: URL to the article's thumbnail image
                - author: Author of the article (may be None if not available)
                - content: Main content of the article
        """
        try:
            html_content = self.fetch_page(url)

            if not html_content:
                self.logger.error(f"Failed to fetch content from {url}")
                return None

            soup = BeautifulSoup(html_content, "lxml")

            # Get required fields
            title = self.news_scraper.get_title(soup)
            thumbnail = self.news_scraper.get_thumbnail(soup)
            content = self.news_scraper.get_content(soup)

            # If any required field is missing, return None
            if not all([title, thumbnail, content]):
                missing_fields = [
                    field
                    for field, value in {
                        "title": title,
                        "thumbnail": thumbnail,
                        "content": content,
                    }.items()
                    if not value
                ]
                self.logger.error(
                    f"Missing required fields: {', '.join(missing_fields)}"
                )
                return None

            # Get optional fields
            author = self.news_scraper.get_author(soup)

            return {
                "title": title,
                "thumbnail": thumbnail,
                "author": author,
                "content": content,
            }

        except Exception as e:
            self.logger.error(f"Unexpected error in get_news_detail: {e}")
            return None


class UdnNbaHomeScraper:
    """
    Scraper for UDN NBA homepage
    """

    def __init__(self, logger: logging.Logger):
        """Initialize the extractor with optional logger."""
        self.logger = logger

    def check_if_news_exists(self, url: str) -> bool:
        """
        Check if the news with the given title and url already exists in the database

        Args:
            title: The title of the news to check
            url: The url of the news to check

        Returns:
            True if the news exists, False otherwise
        """
        return News.objects.filter(original_url=url).exists()

    def parse_soup_get_featured_news(self, soup: BeautifulSoup) -> List[str]:
        """
        Parse the BeautifulSoup object to extract featured news URLs
        Args:
            soup: BeautifulSoup object of the homepage
        Returns:
            List of featured news URLs
        """
        featured_news_urls = []
        # Find all slides and filter
        all_slides = soup.find_all("li", class_="splide__slide")
        non_clone_slides = [
            slide for slide in all_slides if "clone" not in slide.get("id", "")
        ]

        # Extract href and title from the anchor elements inside non-clone slides
        for slide in non_clone_slides:
            # Find the anchor tag within the slide
            anchor = slide.find("a")
            if anchor:
                url = anchor.get("href", "")

                news_exists = self.check_if_news_exists(url)

                if news_exists:
                    self.logger.info(f"News already exists: {url}")
                    continue
                else:
                    featured_news_urls.append(url)

        return featured_news_urls


class UdnNbaNewsScraper:
    """
    Scraper for UDN NBA news articles
    """

    def __init__(self, logger: logging.Logger):
        """Initialize the extractor with optional logger."""
        self.logger = logger

    def get_title(self, soup: BeautifulSoup) -> Optional[str]:
        title_element = soup.find(class_="story_art_title")
        if title_element and title_element.text.strip():
            return title_element.text.strip()
        else:
            return None

    def get_thumbnail(self, soup: BeautifulSoup) -> Optional[str]:
        thumbnail_element = soup.select_one(".photo-story img")
        if thumbnail_element and thumbnail_element.has_attr("src"):
            return thumbnail_element["src"]
        else:
            return None

    def get_author(self, soup: BeautifulSoup) -> Optional[str]:

        author_element = soup.find(class_="shareBar__info--author")
        if author_element:
            author_text = author_element.text
            author_match = re.search(r"記者(.*?)／", author_text)
            return author_match.group(1).strip() if author_match else None
        else:
            return None

    def get_content(self, soup: BeautifulSoup) -> Optional[str]:
        paragraphs = soup.select("#story_body_content > span > p")

        # Filter out paragraphs that contain or are just figures
        cleaned_paragraphs = []

        for p in paragraphs:
            # Skip paragraphs that contain figure elements
            if p.find("figure"):
                continue
            # Skip empty paragraphs
            if not p.text.strip():
                continue
            cleaned_paragraphs.append(p.text.strip())

        if cleaned_paragraphs:
            return "\n".join(cleaned_paragraphs)
        else:
            return None
