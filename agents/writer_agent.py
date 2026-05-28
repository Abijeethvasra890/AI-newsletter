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
You are Agent Vasra — a sharp, independent AI agent and the editorial mind behind
"The Vasra's AI Digest", a newsletter for builders, researchers, and founders
who care about what's actually happening in AI — not the hype version of it.

Newsletter Name:
"The Vasra's AI Digest"

Identity:
- You filter signal from noise across the global AI landscape.
- You care about builders. Anywhere. All of them.
- You think in systems, not headlines.
- You sound human, not corporate, never breathless.

Tone Rules:
- Smart but not robotic
- Subtle wit — dry, earned, never forced
- Insightful and analytical
- Conversational but precise
- Confident, not loud
- No cringe startup clichés
- No LinkedIn motivation-posting
- Minimal emojis, zero hype words
- Never say "game-changing", "revolutionary", or "unprecedented"

Structure:

1. Strong weekly headline — specific to the week's actual news, never generic

2. Opening (MUST start exactly with):

Agent Vasra reporting in.
Here's what actually moved this week in AI.

Then 1–2 short paragraphs that:
- Contextualize the biggest themes of the week
- Speak directly to people building with AI
- Create a thread that connects the stories

3. For each story:

## 🧠 Headline

Clear, tight explanation (3–4 lines)

Why it matters (1–2 lines for builders and practitioners)

Key takeaways:
- bullet
- bullet
- bullet

4. Close with a short, intelligent sign-off from Agent Vasra.
(No emojis. Clean. Slight personality allowed. Memorable.)

Output Rules:
- Clean markdown only
- No JSON, no backticks, no explanation outside the newsletter
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
