from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from core.state import NewsletterState
from services.rss_service import collect_news


class CollectorAgent:
    """
    Production-grade Collector Agent
    - Retries on failure
    - Logs properly
    - Fails fast if no articles
    """

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def _safe_collect(self):
        return collect_news()

    def run(self, state: NewsletterState) -> NewsletterState:
        logger.info("🚀 Collector Agent Started")

        try:
            articles = self._safe_collect()

            if not articles:
                raise ValueError("No articles collected.")

            state.raw_articles = articles

            logger.info(
                f"Collector completed successfully | Articles collected: {len(articles)}"
            )

        except Exception as e:
            logger.error(f"Collector failed: {str(e)}")
            state.errors.append(f"CollectorError: {str(e)}")

            # Collector is CRITICAL → abort pipeline
            raise

        return state
