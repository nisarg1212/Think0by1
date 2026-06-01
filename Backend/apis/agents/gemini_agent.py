import os
from google import genai
from google.genai import types
from apis.agents.base_agent import BaseAgent

class GeminiAgent(BaseAgent):
    def __init__(self):
        # Retrieve the key from the environment variables
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        self.client = genai.Client(api_key=self.api_key)

    def query(self, prompt: str, **kwargs) -> str:
        """
        Queries Gemini 2.5 Flash model with the given prompt.
        """
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
