from dataclasses import dataclass, field, replace
from typing import Dict, Any, Optional

@dataclass(frozen=True)
class AgentState:
    """Holds the immutable state for a single agent's contribution."""
    draft: Optional[str] = None
    score: Optional[float] = None
    critique: Optional[str] = None
    corrected_answer: Optional[str] = None
    final_answer: Optional[str] = None

    def update(self, **kwargs) -> 'AgentState':
        return replace(self, **kwargs)

@dataclass(frozen=True)
class OrchestrationState:
    """
    Immutable state of the orchestration graph.
    Nodes return a state delta or a new state copy using state.update().
    """
    question_id: int
    prompt: str
    
    # Map of agent names to their individual states
    agent_states: Dict[str, AgentState] = field(default_factory=dict)
    
    # Final synthesized answer
    blended_result: Optional[str] = None
    
    # Extensible metadata dictionary (retries, dynamic path selections, etc.)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def update(self, **kwargs) -> 'OrchestrationState':
        """Creates a new copy of OrchestrationState with updated values."""
        # Deep copy metadata and agent_states to ensure state immutability
        if 'metadata' in kwargs:
            kwargs['metadata'] = {**self.metadata, **kwargs['metadata']}
        else:
            kwargs['metadata'] = self.metadata.copy()

        if 'agent_states' in kwargs:
            kwargs['agent_states'] = {**self.agent_states, **kwargs['agent_states']}
        else:
            kwargs['agent_states'] = self.agent_states.copy()

        return replace(self, **kwargs)

    def update_agent_state(self, agent_name: str, **kwargs) -> 'OrchestrationState':
        """Helper to return a new OrchestrationState with a specific agent's state updated."""
        current_agent_state = self.agent_states.get(agent_name, AgentState())
        new_agent_state = current_agent_state.update(**kwargs)
        
        new_agent_states = {**self.agent_states, agent_name: new_agent_state}
        return self.update(agent_states=new_agent_states)
