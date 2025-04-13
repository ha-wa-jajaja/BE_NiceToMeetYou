from celery import shared_task
from django.db import transaction
from news.models import News, NewsSession
from news.scrape.parsers import UdnNbaParsers
from news.scrape.scrapers import UdnNbaScraper


@shared_task
def fetch_news():
    """Main task that initiates scraping and spawns subtasks"""
    scraper = UdnNbaScraper()

    # Get all news URLs
    new_featured_news = scraper.get_homepage_featured_news_urls()

    if not new_featured_news:
        return "No new news"

    # Create a session
    with transaction.atomic():
        news_session = NewsSession.objects.create()
        session_id = news_session.id

    # Spawn individual tasks for each URL
    for url in new_featured_news:
        process_news_article.delay(url, session_id)

    return f"Started processing {len(new_featured_news)} news articles"


@shared_task
def process_news_article(url, session_id):
    """Process a single news article"""
    scraper = UdnNbaScraper()
    parser = UdnNbaParsers()

    # Get the session
    try:
        news_session = NewsSession.objects.get(id=session_id)
    except NewsSession.DoesNotExist:
        return f"Session {session_id} not found"

    # Get news details
    news_detail = scraper.get_news_detail(url)
    if not news_detail:
        return f"Failed to retrieve news detail for {url}"

    # Process the news article
    with transaction.atomic():
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

    return f"Processed news: {news.title}"
