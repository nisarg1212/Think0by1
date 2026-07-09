import time
from typing import Callable, Optional, Dict, Any, List
from apis.engine.graph_def import GraphDefinition
from apis.engine.state import OrchestrationState
from apis.engine.context import ExecutionContext

class GraphEngine:
    """
    Coordinates state updates, routing, step callbacks, and execution metrics.
    """
    def __init__(self, graph_def: GraphDefinition):
        self.graph = graph_def

    async def execute(
        self,
        initial_state: OrchestrationState,
        context: ExecutionContext,
        on_node_start: Optional[Callable[[str, OrchestrationState], None]] = None,
        on_node_end: Optional[Callable[[str, OrchestrationState], None]] = None
    ) -> OrchestrationState:
        """
        Runs the graph execution loop sequentially.
        """
        if not self.graph.entry_point:
            raise ValueError("Graph has no entry point defined.")

        state = initial_state
        current_node = self.graph.entry_point
        
        # Telemetry metrics collection (extensibility)
        metrics: List[Dict[str, Any]] = []
        context.metadata["steps"] = metrics

        while current_node:
            node_fn = self.graph.nodes.get(current_node)
            if not node_fn:
                raise ValueError(f"Node '{current_node}' is defined in structure but has no registered action.")

            # Trigger Start Callback
            if on_node_start:
                on_node_start(current_node, state)

            context.logger.info(f"Executing node: {current_node}")
            start_time = time.time()
            
            # Execute pure node function
            try:
                state = await node_fn(state, context)
            except Exception as e:
                context.logger.error(f"Node {current_node} failed with exception: {e}")
                raise e
            
            execution_time = time.time() - start_time
            metrics.append({
                "node": current_node,
                "execution_seconds": execution_time
            })

            # Trigger End Callback
            if on_node_end:
                on_node_end(current_node, state)

            # Routing Logic
            if current_node in self.graph.conditional_edges:
                router_fn = self.graph.conditional_edges[current_node]
                next_node = router_fn(state, context)
                context.logger.info(f"Conditional router from {current_node} returned next node: {next_node}")
                current_node = next_node
            else:
                next_node = self.graph.edges.get(current_node)
                context.logger.info(f"Static transition from {current_node} to next node: {next_node}")
                current_node = next_node

        return state
