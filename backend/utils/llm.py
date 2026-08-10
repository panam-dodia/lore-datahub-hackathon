import os

from groq import Groq


class LLMClient:
    """Thin wrapper around the Groq chat completions API."""

    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    async def complete(self, prompt: str) -> str:
        """Send a single-turn prompt and return the raw text response."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return response.choices[0].message.content
