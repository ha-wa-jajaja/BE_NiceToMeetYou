"""
UDN NBA News Scraper Module
"""

import logging
import re
from typing import Dict, List, Optional, Tuple, Union

import requests
from bs4 import BeautifulSoup
from django.utils import timezone

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("news_scraper")


class UdnNbaScraper:
    """Scraper for UDN NBA website"""

    BASE_URL = "https://tw-nba.udn.com/nba"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    def __init__(self):
        """Initialize scraper with default configuration"""
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch HTML content from the given URL

        Args:
            url: The URL to fetch

        Returns:
            HTML content or None if an error occurs
        """
        try:
            logger.info(f"Fetching URL: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None

    def extract_featured_news(self) -> List[Dict[str, Union[str, List[str]]]]:
        """
        Extract featured news from UDN NBA website

        Returns:
            List of dictionaries containing news data
        """
        featured_news = []
        html_content = self.fetch_page(f"{self.BASE_URL}/index")

        if not html_content:
            logger.error("Failed to fetch the main page")
            return featured_news

        soup = BeautifulSoup(html_content, "lxml")

        # Extract featured news section
        featured_section = soup.select(".tab-content .news-list")
        if not featured_section:
            logger.error("Featured news section not found")
            return featured_news

        # Extract news items
        news_items = featured_section[0].select("dt")
        logger.info(f"Found {len(news_items)} featured news items")

        for item in news_items:
            try:
                # Extract title and link
                title_elem = item.select_one("a")
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                link = title_elem.get("href")
                full_link = f"{self.BASE_URL}/{link}" if link else None

                if not full_link:
                    continue

                # Extract thumbnail
                img_elem = item.select_one("img")
                thumbnail = img_elem.get("src") if img_elem else None

                # Get news details (content, author, etc.)
                article_data = self.extract_article_data(full_link)

                news_data = {
                    "title": title,
                    "url": full_link,
                    "thumbnail_url": thumbnail,
                    "content": article_data.get("content", ""),
                    "author": article_data.get("author", "Unknown"),
                    "tags": article_data.get("tags", []),
                }

                featured_news.append(news_data)
                logger.info(f"Extracted: {title}")

            except Exception as e:
                logger.error(f"Error extracting news item: {str(e)}")
                continue

        return featured_news

    def extract_article_data(
        self, article_url: str
    ) -> Dict[str, Union[str, List[str]]]:
        """
        Extract data from a single article page

        Args:
            article_url: URL of the article to extract data from

        Returns:
            Dictionary with article content, author and tags
        """
        article_data = {"content": "", "author": "Unknown", "tags": []}

        html_content = self.fetch_page(article_url)
        if not html_content:
            return article_data

        soup = BeautifulSoup(html_content, "lxml")

        # Extract content
        content_elem = soup.select_one(".article-content")
        if content_elem:
            article_data["content"] = content_elem.get_text(strip=True)

        # Extract author
        author_elem = soup.select_one(".article-content p.dis")
        if author_elem:
            author_text = author_elem.get_text(strip=True)
            author_match = re.search(r"[◎／]([^／]+)", author_text)
            if author_match:
                article_data["author"] = author_match.group(1).strip()

        # Extract tags
        # Determine if content mentions any teams or players from the tags model
        # This requires integrating with the tags model, which we'll do in the task

        return article_data

    def scrape_featured_news(self) -> List[Dict[str, Union[str, List[str]]]]:
        """
        Main entry point for scraping featured news

        Returns:
            List of scraped news articles
        """
        try:
            logger.info(f"Starting scraping at {timezone.now()}")
            featured_news = self.extract_featured_news()
            logger.info(f"Completed scraping. Found {len(featured_news)} articles")
            return featured_news
        except Exception as e:
            logger.error(f"Error during scraping: {str(e)}")
            return []


# Example usage when running the module directly
if __name__ == "__main__":
    scraper = UdnNbaScraper()
    news = scraper.scrape_featured_news()

    for i, item in enumerate(news, 1):
        print(f"\nArticle {i}:")
        print(f"Title: {item['title']}")
        print(f"URL: {item['url']}")
        print(f"Thumbnail: {item['thumbnail_url']}")
        print(f"Author: {item['author']}")
        print(f"Content preview: {item['content'][:100]}...")
