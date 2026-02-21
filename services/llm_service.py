import os
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential


class LLMService:

    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    def generate(self, messages, model="llama3-70b"):
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3
        )
        return response.choices[0].message.content
