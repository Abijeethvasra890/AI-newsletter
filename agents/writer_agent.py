from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from core.state import NewsletterState
from services.llm_router import LLMRouter


class WriterAgent:

    def __init__(self):
        self.llm = LLMRouter()

    def _build_prompt(self, state: NewsletterState) -> str:

        articles_text = "\n\n".join([
            f"""
TITLE: {a.title}

SUMMARY:
{a.summary}

WHY IT MATTERS:
{a.why_it_matters}

KEY POINTS:
{chr(10).join([f"- {kp}" for kp in a.key_points])}
"""
            for a in state.processed_articles
        ])

        return f"""
You are Gradya — an intelligent, slightly witty AI agent writing
a weekly AI newsletter for Indian developers and startup founders.

Newsletter Name:
"The Backprop Bulletin"

Tone Rules:
- Smart but not robotic
- Slight humor (subtle, intelligent)
- Insightful
- Conversational but sharp
- Avoid cringe startup clichés
- Avoid sounding like LinkedIn
- No excessive emojis

Structure:

1. Catchy headline for the week
2. Engaging intro (2–3 short paragraphs)
3. For each story:

## 🧠 Headline

Short engaging explanation (3–4 lines)

Why it matters (1–2 lines)

Key takeaways:
- bullet
- bullet
- bullet

4. End with a witty sign-off from Gradya

Output:
- Clean markdown
- No JSON
- No explanation outside newsletter
- No backticks

Articles to include:

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
            temperature=0.7  # More creative
        )

    def run(self, state: NewsletterState) -> NewsletterState:

        logger.info("✍️ Writer Agent Started")

        if not state.processed_articles:
            raise ValueError("Writer received empty processed_articles")

        try:
            prompt = self._build_prompt(state)
            raw_output = self._call_llm(prompt)

            cleaned = raw_output.strip().replace("```", "")

            state.final_newsletter = cleaned

            logger.info("Writer successfully generated newsletter")

        except Exception as e:
            logger.error(f"Writer failed: {str(e)}")
            state.errors.append(f"WriterError: {str(e)}")
            raise

        return state
