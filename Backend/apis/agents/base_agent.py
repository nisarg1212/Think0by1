from abc import ABC, abstractmethod

class BaseAgent(ABC):
    @abstractmethod
    def query(self, prompt: str, **kwargs) -> str:
        """
        Sends a query prompt to the agent's respective LLM API.
        Returns the text response as a string.
        """
        pass
