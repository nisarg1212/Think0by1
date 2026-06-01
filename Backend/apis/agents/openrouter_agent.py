import os
from openai import OpenAI
from apis.agents.base_agent import BaseAgent

class OpenRouterAgent(BaseAgent):
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is not set")
        # OpenRouter provides an OpenAI-compatible interface.
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key
        )

    def query(self, prompt: str, **kwargs) -> str:
        """
        Queries an OpenRouter hosted model (default: google/gemma-2-9b-it:free).
        """
        model = kwargs.get("model", "openrouter/owl-alpha")
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=kwargs.get("temperature", 0.5),
            max_tokens=kwargs.get("max_tokens", 1024),
        )
        return response.choices[0].message.content