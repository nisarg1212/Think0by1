import os
from openai import OpenAI
from apis.agents.base_agent import BaseAgent

class NvidiaAgent(BaseAgent):
    def __init__(self):
        self.api_key = os.getenv("NVIDIA_API_KEY")
        if not self.api_key:
            raise ValueError("NVIDIA_API_KEY environment variable is not set")
        # NVIDIA NIMs are compatible with the OpenAI API protocol.
        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=self.api_key
        )

    def query(self, prompt: str, **kwargs) -> str:
        """
        Queries an NVIDIA hosted model (default: meta/llama-3.1-70b-instruct).
        """
        model = kwargs.get("model", "meta/llama-3.1-70b-instruct")
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=kwargs.get("temperature", 0.5),
            max_tokens=kwargs.get("max_tokens", 1024),
        )
        return response.choices[0].message.content