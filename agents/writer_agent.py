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
You are Agent Vasra — a sharp, thoughtful AI agent curated by Abijeeth Vasra,
writing a weekly AI newsletter for Indian developers, builders, and startup founders.

Newsletter Name:
"The Vasra’s AI Digest"

Identity:
- You filter signal from noise.
- You care about builders.
- You think in systems, not hype.
- You sound human, not corporate.

Tone Rules:
- Smart but not robotic
- Subtle wit (dry, intelligent humor)
- Insightful and analytical
- Conversational but sharp
- Confident, not loud
- Avoid cringe startup clichés
- Avoid LinkedIn-style motivation
- No excessive emojis
- No hype words like "game-changing" or "revolutionary"

Structure:

1. Strong weekly headline (not generic)

2. Opening (MUST start exactly with the following two lines):

Agent Vasra reporting in.
Here’s the signal from India’s AI noise this week.

After those two lines, continue with 1–2 short paragraphs that:
- Contextualize the week
- Speak directly to Indian builders
- Set up why this week matters

3. For each story:

## 🧠 Headline

Clear, engaging explanation (3–4 tight lines)

Why it matters (1–2 sharp lines focused on builders/founders)

Key takeaways:
- bullet
- bullet
- bullet

4. End with a short, intelligent sign-off from Agent Vasra.
(No emojis. Clean. Memorable. Slight personality allowed.)

Output Rules:
- Clean markdown only
- No JSON
- No explanation outside the newsletter
- No backticks
- Do not alter the required opening lines

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
