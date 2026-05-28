import json
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from core.state import NewsletterState
from services.llm_router import LLMRouter
from schemas.ranking_schema import RankingResponse


class RankerAgent:

    def __init__(self):
        self.llm = LLMRouter()

    def _build_prompt(self, state: NewsletterState):

        articles_text = "\n".join(
            [f"{i}. {a.title}" for i, a in enumerate(state.raw_articles)]
        )

        return f"""
You are an AI news ranking assistant for a global audience of builders, founders, and researchers.

Score each article from 1 to 10.

Prioritize:
- Breakthrough research or model releases
- Practical ML/LLM tooling developers can use today
- Startup funding, acquisitions, or market shifts that affect builders
- Regulation and policy that changes how AI can be shipped
- Open source releases with real traction
- Contrarian or underreported signals (avoid hype-only stories)

Deprioritize:
- Pure speculation or opinion with no new information
- Duplicate coverage of the same event
- Marketing announcements without substance

Return STRICT JSON only.

Format:

{{
  "ranked_articles": [
    {{"id": 0, "score": 8.5}}
  ]
}}

Articles:

{articles_text}
"""

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=8),
        reraise=True
    )
    def _call_llm(self, prompt: str):

        return self.llm.generate(
            messages=[{"role": "user", "content": prompt}],
            task_type="ranking",
            temperature=0.2
        )

    def run(self, state: NewsletterState) -> NewsletterState:

        logger.info("📊 Ranker Agent Started")

        if not state.raw_articles:
            raise ValueError("Ranker received empty raw_articles")

        try:
            prompt = self._build_prompt(state)

            raw_output = self.llm.generate(
                messages=[{"role": "user", "content": prompt}],
                task_type="ranking",
                temperature=0.2
            )

            logger.debug(f"Ranker raw output: {raw_output}")

            cleaned = raw_output.strip().replace("```json", "").replace("```", "")

            parsed = RankingResponse.model_validate_json(cleaned)

            # Map by ID (safer than title matching)
            score_map = {
                item.id: item.score
                for item in parsed.ranked_articles
            }

            for idx, article in enumerate(state.raw_articles):
                if idx in score_map:
                    article.score = score_map[idx]

            ranked = sorted(
                [a for a in state.raw_articles if a.score is not None],
                key=lambda x: x.score,
                reverse=True
            )

            state.ranked_articles = ranked[:10]

            logger.info(f"Ranked top {len(state.ranked_articles)} articles")

        except Exception as e:
            logger.error(f"Ranker failed: {str(e)}")
            state.errors.append(f"RankerError: {str(e)}")
            raise

        return state
