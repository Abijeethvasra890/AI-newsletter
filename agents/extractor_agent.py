import json
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from core.state import NewsletterState
from services.llm_router import LLMRouter
from schemas.extraction_schema import ExtractionResponse


class ExtractorAgent:

    def __init__(self):
        self.llm = LLMRouter()

    def _build_prompt(self, state: NewsletterState):

        articles_text = "\n\n".join([
            f"""
ID: {i}
TITLE: {a.title}
CONTENT:
{
    getattr(a, "content", None)
    or getattr(a, "description", None)
    or "No content available"
}
"""
            for i, a in enumerate(state.ranked_articles)
        ])

        return f"""
You are an AI newsletter content analyst.

For each article, generate:

- A concise 3–4 line summary
- Why it matters for Indian AI developers/startups
- 3 key bullet points

Return STRICT JSON.

Format:

{{
  "articles": [
    {{
      "id": 0,
      "summary": "...",
      "why_it_matters": "...",
      "key_points": ["...", "...", "..."]
    }}
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
            task_type="writing",
            temperature=0.4
        )

    def run(self, state: NewsletterState) -> NewsletterState:

        logger.info("📝 Extractor Agent Started")

        if not state.ranked_articles:
            raise ValueError("Extractor received empty ranked_articles")

        try:
            prompt = self._build_prompt(state)
            raw_output = self._call_llm(prompt)

            logger.debug(f"Extractor raw output: {raw_output}")

            cleaned = raw_output.strip().replace("```json", "").replace("```", "")

            parsed = ExtractionResponse.model_validate_json(cleaned)

            valid_ids = set(range(len(state.ranked_articles)))

            processed = []

            for item in parsed.articles:
                if item.id in valid_ids:
                    article = state.ranked_articles[item.id]

                    article.summary = item.summary
                    article.why_it_matters = item.why_it_matters
                    article.key_points = item.key_points

                    processed.append(article)

            state.processed_articles = processed

            logger.info(f"Extractor processed {len(processed)} articles")

        except Exception as e:
            logger.error(f"Extractor failed: {str(e)}")
            state.errors.append(f"ExtractorError: {str(e)}")
            raise

        return state
