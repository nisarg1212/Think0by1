from typing import Dict, Any, Optional
import logging
from apis.agents.base_agent import BaseAgent
from apis.services.judge import ResponseJudge

class ExecutionContext:
    """
    Decouples environmental dependencies from the StateGraph engine.
    Holds reference to API clients, judges, configuration, and logging.
    """
    def __init__(
        self,
        agents: Dict[str, BaseAgent],
        judge: ResponseJudge,
        config: Optional[Dict[str, Any]] = None,
        logger: Optional[logging.Logger] = None
    ):
        self.agents = agents
        self.judge = judge
        self.config = config or {}
        self.metadata = {}
        self.logger = logger or logging.getLogger("StateGraphEngine")
