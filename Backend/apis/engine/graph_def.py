from typing import Dict, Callable, Optional, Any

class GraphDefinition:
    """
    Declarative representation of the state graph's structure.
    Separates graph definition from execution logic.
    """
    def __init__(self):
        self.nodes: Dict[str, Callable] = {}
        self.edges: Dict[str, str] = {}
        self.conditional_edges: Dict[str, Callable[[Any, Any], str]] = {}
        self.entry_point: Optional[str] = None

    def add_node(self, name: str, node_fn: Callable) -> 'GraphDefinition':
        self.nodes[name] = node_fn
        return self

    def add_edge(self, start_node: str, end_node: str) -> 'GraphDefinition':
        self.edges[start_node] = end_node
        return self

    def add_conditional_edge(self, start_node: str, router_fn: Callable[[Any, Any], str]) -> 'GraphDefinition':
        self.conditional_edges[start_node] = router_fn
        return self

    def set_entry_point(self, name: str) -> 'GraphDefinition':
        if name not in self.nodes:
            raise ValueError(f"Entry point '{name}' must be an registered node.")
        self.entry_point = name
        return self
