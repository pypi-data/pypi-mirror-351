"""
Graph export functionality for Tracegraph.
"""

import os
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class TraceNode:
    """Node in the trace graph representing a function call."""
    name: str
    args: Dict[str, Any]
    returns: Any
    start_time: float
    end_time: float
    children: List['TraceNode'] = field(default_factory=list)
    error: Optional[Exception] = None
    is_generator: bool = False
    yielded_values: List[Any] = field(default_factory=list)

class TraceGraph:
    """Handles conversion of trace data to Graphviz format."""
    
    def __init__(self):
        self.nodes: list[TraceNode] = []
        self.current_node: Optional[TraceNode] = None
        self.node_stack: list[TraceNode] = []
    
    def add_node(self, function_name: str, args: Dict[str, Any], 
                return_value: Any, execution_time: float, depth: int) -> None:
        """Add a new node to the trace graph."""
        node = TraceNode(
            name=function_name,
            args=args,
            returns=return_value,
            start_time=execution_time,
            end_time=execution_time,
            children=[],
            error=None,
            is_generator=False,
            yielded_values=[]
        )
        
        if not self.node_stack:  # Root node
            self.nodes.append(node)
        else:
            self.node_stack[-1].children.append(node)
        
        self.current_node = node
        self.node_stack.append(node)
    
    def pop_node(self) -> None:
        """Remove the current node from the stack."""
        if self.node_stack:
            self.node_stack.pop()
            self.current_node = self.node_stack[-1] if self.node_stack else None
    
    def to_dot(self, title: str = "Function Call Trace") -> str:
        """Convert the trace to Graphviz DOT format."""
        dot = [
            "digraph G {",
            f'    label="{title}";',
            "    node [shape=box, style=filled, fontname=\"Arial\"];",
            "    edge [fontname=\"Arial\"];",
            "",
            "    // Node styles",
            "    node [fillcolor=\"#e6f3ff\", color=\"#0066cc\"];",  # Default style
            "    edge [color=\"#666666\"];",
            "",
            "    // Time-based node colors",
            "    node [fillcolor=\"#e6ffe6\", color=\"#006600\"] [label=\"Fast (≤1s)\"];",
            "    node [fillcolor=\"#fff2e6\", color=\"#cc6600\"] [label=\"Medium (1-5s)\"];",
            "    node [fillcolor=\"#ffe6e6\", color=\"#cc0000\"] [label=\"Slow (>5s)\"];",
            ""
        ]
        
        # Add nodes and edges
        def add_node(node: TraceNode, parent_id: Optional[str] = None) -> None:
            # Create node label
            args_str = ", ".join(f"{k}={v!r}" for k, v in node.args.items())
            time_str = f"took {self._format_time(node.end_time - node.start_time)}"
            
            # Determine node color based on execution time
            if node.end_time - node.start_time <= 1:
                color = "#e6ffe6"  # Light green
                edge_color = "#006600"  # Dark green
            elif node.end_time - node.start_time <= 5:
                color = "#fff2e6"  # Light orange
                edge_color = "#cc6600"  # Dark orange
            else:
                color = "#ffe6e6"  # Light red
                edge_color = "#cc0000"  # Dark red
            
            # Create node ID
            node_id = f"node_{id(node)}"
            
            # Add node
            dot.append(f'    {node_id} [')
            dot.append(f'        label="{node.name}({args_str})\\n{time_str}\\nreturns: {node.returns!r}";')
            dot.append(f'        fillcolor="{color}";')
            dot.append(f'        color="{edge_color}";')
            dot.append("    ];")
            
            # Add edge from parent
            if parent_id:
                dot.append(f'    {parent_id} -> {node_id} [color="{edge_color}"];')
            
            # Add children
            for child in node.children:
                add_node(child, node_id)
        
        # Add all root nodes
        for node in self.nodes:
            add_node(node)
        
        dot.append("}")
        return "\n".join(dot)
    
    def save_dot(self, filename: str, title: str = "Function Call Trace") -> None:
        """Save the trace as a DOT file."""
        with open(filename, "w") as f:
            f.write(self.to_dot(title))
    
    def save_png(self, filename: str, title: str = "Function Call Trace") -> None:
        """Save the trace as a PNG file using Graphviz."""
        try:
            import graphviz
        except ImportError:
            raise ImportError(
                "Graphviz is required for PNG export. "
                "Install it with: pip install tracegraph[graphviz]"
            )
        
        # Create a temporary DOT file
        dot_filename = f"{filename}.dot"
        self.save_dot(dot_filename, title)
        
        # Convert DOT to PNG
        graph = graphviz.Source.from_file(dot_filename)
        graph.render(filename, format="png", cleanup=True)
        
        # Clean up the temporary DOT file
        os.remove(dot_filename)
    
    def _format_time(self, seconds: float) -> str:
        """Format time in appropriate units."""
        if seconds < 0.001:  # Less than 1ms
            return f"{seconds * 1_000_000:.2f} microseconds"
        elif seconds < 1:  # Less than 1s
            return f"{seconds * 1000:.2f} milliseconds"
        elif seconds < 60:  # Less than 1min
            return f"{seconds:.2f} seconds"
        elif seconds < 3600:  # Less than 1hour
            minutes = seconds / 60
            return f"{minutes:.2f} minutes"
        else:  # Hours or more
            hours = seconds / 3600
            return f"{hours:.2f} hours" 