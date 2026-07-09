from abc import ABC, abstractmethod
import asyncio

class BaseAgent(ABC):
    @abstractmethod
    def query(self, prompt: str, **kwargs) -> str:
        """
        Sends a query prompt to the agent's respective LLM API.
        Returns the text response as a string.
        """
        pass

    async def async_query(self, prompt: str, **kwargs) -> str:
        """
        Asynchronous wrapper for the query method.
        By default, it runs the synchronous query in a background thread to prevent blocking.
        Subclasses can override this with native async client calls if available.
        """
        return await asyncio.to_thread(self.query, prompt, **kwargs)
