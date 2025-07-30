"""
Tracegraph - Visualize Python function calls as call trees
"""

__version__ = "0.1.0"

from .tracer import trace, Colors, save_trace, trace_module

__all__ = ["trace", "Colors", "save_trace", "trace_module"] 