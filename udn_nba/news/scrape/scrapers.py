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

    def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch HTML content from the given URL

        Args:
            url: The URL to fetch

        Returns:
            HTML content or None if an error occurs
        """
        try:
            self.logger.info(f"Fetching URL: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            self.logger.error(f"Error fetching {url}: {str(e)}")
            return None

    def check_if_news_exists(self, title: str, url: str) -> bool:
        """
        Check if the news with the given title and url already exists in the database

        Args:
            title: The title of the news to check
            url: The url of the news to check

        Returns:
            True if the news exists, False otherwise
        """
        return News.objects.filter(title=title, original_url=url).exists()

    def get_homepage_featured_news_urls(self) -> List[str]:
        """
        Extract featured news from the homepage

        Returns:
            List of dictionaries containing news urls
        """
        featured_news_urls = []
        html_content = self.fetch_page(self.BASE_URL)

        if not html_content:
            self.logger.error(f"Failed to fetch content from {self.BASE_URL}")
            return featured_news_urls

        soup = BeautifulSoup(html_content, "lxml")

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
                title = anchor.get("title", "")
                url = anchor.get("href", "")

                news_exists = self.check_if_news_exists(title, url)
                if news_exists:
                    self.logger.info(f"News already exists: {url}")
                    continue
                else:
                    featured_news_urls.append(url)

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

            # Initialize result with None values
            result = {"title": None, "thumbnail": None, "author": None, "content": None}

            # Get title (required)
            try:
                title_element = soup.find(class_="story_art_title")
                if title_element and title_element.text.strip():
                    result["title"] = title_element.text.strip()
                else:
                    self.logger.error(f"Required title element not found at {url}")
                    return None
            except Exception as e:
                self.logger.error(f"Error extracting title: {e}")
                return None

            # Get thumbnail (required)
            try:
                thumbnail_element = soup.select_one(".photo-story img")
                if thumbnail_element and thumbnail_element.has_attr("src"):
                    result["thumbnail"] = thumbnail_element["src"]
                else:
                    self.logger.error(f"Required thumbnail not found at {url}")
                    return None
            except Exception as e:
                self.logger.error(f"Error extracting thumbnail: {e}")
                return None

            # Get Author (optional)
            try:
                author_element = soup.find(class_="shareBar__info--author")
                if author_element:
                    author_text = author_element.text
                    author_match = re.search(r"記者(.*?)／", author_text)
                    result["author"] = (
                        author_match.group(1).strip() if author_match else None
                    )
                    # No return None here as the author is optional
            except Exception as e:
                self.logger.warning(f"Error extracting author: {e}")
                # Still proceed with None for author

            # Get Content (required)
            try:
                paragraphs = soup.select("#story_body_content p")
                if paragraphs:
                    result["content"] = "\n".join([p.text.strip() for p in paragraphs])
                    if not result[
                        "content"
                    ].strip():  # Check if content is just whitespace
                        self.logger.error(f"Required content is empty at {url}")
                        return None
                else:
                    self.logger.error(f"Required content paragraphs not found at {url}")
                    return None
            except Exception as e:
                self.logger.error(f"Error extracting content: {e}")
                return None

            return result

        except Exception as e:
            self.logger.error(f"Unexpected error in get_news_detail: {e}")
            return None
