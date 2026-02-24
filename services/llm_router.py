import os
import time
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from groq import Groq
#import google.generativeai as genai

from dotenv import load_dotenv
load_dotenv()



class LLMRouter:

    def __init__(self):
        self.groq_client = None
        self.gemini_model = None

        if os.getenv("GROQ_API_KEY"):
            self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            logger.info("Groq initialized")

        #if os.getenv("GEMINI_API_KEY"):
         #   genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
          #  self.gemini_model = genai.GenerativeModel("gemini-2.0-flash-lite")
           # logger.info("Gemini initialized")

        if not self.groq_client and not self.gemini_model:
            raise RuntimeError("No LLM provider configured.")

    # -------------------------------
    # Provider Selection Strategy
    # -------------------------------
    def _select_provider(self, task_type: str):
        if task_type in ["ranking", "writing", "quality"] and self.groq_client:
            return "groq"

        # if task_type in ["writing", "quality"] and self.gemini_model:
        #     return "gemini"

        # fallback priority
        if self.groq_client:
            return "groq"

        if self.gemini_model:
            return "gemini"

        raise RuntimeError("No available provider.")

    # -------------------------------
    # Main Generation Function
    # -------------------------------
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=8),
        reraise=True
    )
    def generate(self, messages, task_type="ranking", temperature=0.2):

        provider = self._select_provider(task_type)
        logger.info(f"Using provider: {provider}")

        start = time.time()

        try:
            if provider == "groq":
                response = self.groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    temperature=temperature,
                    timeout=30
                )

                output = response.choices[0].message.content

            elif provider == "gemini":
                # Preserve role structure properly
                prompt = "\n".join(
                    [f"{m['role'].upper()}: {m['content']}" for m in messages]
                )

                response = self.gemini_model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": temperature
                    }
                )

                output = response.text

            else:
                raise RuntimeError("Invalid provider")

            latency = round(time.time() - start, 2)
            logger.info(f"LLM latency: {latency}s")

            return output.strip()

        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise
