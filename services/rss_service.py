import feedparser
import requests
from datetime import datetime
from typing import List
from loguru import logger
from core.constants import AI_RSS_FEEDS, MAX_ARTICLES_PER_FEED
from core.state import Article


def normalize_entry(entry, source_name: str) -> Article:
    return Article(
        title=entry.get("title", "").strip(),
        url=entry.get("link", ""),
        source=source_name,
        published_at=str(entry.get("published", datetime.utcnow()))
    )


def fetch_feed(url: str) -> List[Article]:
    logger.info(f"Fetching RSS feed: {url}")

    parsed = feedparser.parse(url)

    articles = []
    source_name = parsed.feed.get("title", url)

    for entry in parsed.entries[:MAX_ARTICLES_PER_FEED]:
        try:
            article = normalize_entry(entry, source_name)
            if article.title and article.url:
                articles.append(article)
        except Exception as e:
            logger.warning(f"Failed to parse entry: {e}")

    logger.info(f"Fetched {len(articles)} from {source_name}")
    return articles


def deduplicate(articles: List[Article]) -> List[Article]:
    seen = set()
    unique_articles = []

    for article in articles:
        key = (article.title.lower(), article.url)
        if key not in seen:
            seen.add(key)
            unique_articles.append(article)

    logger.info(f"Deduplicated to {len(unique_articles)} articles")
    return unique_articles


def filter_basic_relevance(articles: List[Article]) -> List[Article]:
    keywords = ["ai", "artificial", "machine", "llm", "ml", "deep learning"]

    filtered = [
        article for article in articles
        if any(k in article.title.lower() for k in keywords)
    ]

    logger.info(f"Filtered to {len(filtered)} relevant articles")
    return filtered


def collect_news() -> List[Article]:
    all_articles = []

    for feed in AI_RSS_FEEDS:
        try:
            articles = fetch_feed(feed)
            all_articles.extend(articles)
        except Exception as e:
            logger.error(f"Feed failed: {feed} | Error: {e}")

    all_articles = deduplicate(all_articles)
    all_articles = filter_basic_relevance(all_articles)

    return all_articles
