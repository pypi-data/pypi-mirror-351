"""
Core tracing functionality for Tracegraph.
"""

import functools
import inspect
import threading
import time
from typing import Any, Callable, Optional, TypeVar, Dict, Union
from .graph import TraceGraph

# Type variable for generic function type
F = TypeVar('F', bound=Callable[..., Any])

# Thread-local storage for call depth
_call_depth = threading.local()

# Global trace graph
_trace_graph = TraceGraph()

# ANSI color codes
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

# Default color scheme
DEFAULT_COLORS = {
    "function": Colors.CYAN,
    "args": Colors.WHITE,
    "returns": Colors.GREEN,
    "error": Colors.RED,
    "tree": Colors.BLUE,
    "time_fast": Colors.GREEN,    # ≤ 1s
    "time_medium": Colors.YELLOW, # 1s - 5s
    "time_slow": Colors.RED,      # > 5s
}

def _format_time(seconds: float) -> str:
    """Format time in appropriate units with color."""
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

def _get_time_color(seconds: float, colors: Dict[str, str]) -> str:
    """Get appropriate color for time based on duration."""
    # Use default time colors if custom colors don't include them
    if seconds <= 1:  # Fast: ≤ 1s
        return colors.get("time_fast", DEFAULT_COLORS["time_fast"])
    elif seconds <= 5:  # Medium: 1s - 5s
        return colors.get("time_medium", DEFAULT_COLORS["time_medium"])
    else:  # Slow: > 5s
        return colors.get("time_slow", DEFAULT_COLORS["time_slow"])

def _get_call_depth() -> int:
    """Get the current call depth for the thread."""
    if not hasattr(_call_depth, 'depth'):
        _call_depth.depth = 0
    return _call_depth.depth

def _increment_depth() -> None:
    """Increment the call depth for the thread."""
    _call_depth.depth = _get_call_depth() + 1

def _decrement_depth() -> None:
    """Decrement the call depth for the thread."""
    _call_depth.depth = max(0, _get_call_depth() - 1)

def _format_args(args: tuple, kwargs: dict) -> str:
    """Format function arguments into a readable string."""
    # Get the function signature
    sig = inspect.signature(args[0].__wrapped__ if hasattr(args[0], '__wrapped__') else args[0])
    
    # Bind the arguments to the signature
    bound_args = sig.bind(*args[1:], **kwargs)
    bound_args.apply_defaults()
    
    # Format the arguments
    arg_strs = []
    for name, value in bound_args.arguments.items():
        # Truncate long values
        if isinstance(value, (str, bytes)):
            value = str(value)[:50] + '...' if len(str(value)) > 50 else value
        arg_strs.append(f"{name}={value!r}")
    
    return ", ".join(arg_strs)

def _get_args_dict(args: tuple, kwargs: dict) -> Dict[str, Any]:
    """Get function arguments as a dictionary."""
    # Get the function signature
    sig = inspect.signature(args[0].__wrapped__ if hasattr(args[0], '__wrapped__') else args[0])
    
    # Bind the arguments to the signature
    bound_args = sig.bind(*args[1:], **kwargs)
    bound_args.apply_defaults()
    
    return dict(bound_args.arguments)

def _colorize(text: str, color: str, use_colors: bool = True, bold: bool = False) -> str:
    """Add color to text if colors are enabled."""
    if not use_colors:
        return text
    if bold:
        return f"{Colors.BOLD}{color}{text}{Colors.RESET}"
    return f"{color}{text}{Colors.RESET}"

def trace(
    func: Optional[F] = None,
    *,
    show_args: bool = True,
    use_colors: bool = True,
    colors: Optional[Dict[str, str]] = None,
    show_time: bool = False
) -> F:
    """
    Decorator that traces function calls and their return values.
    
    Args:
        func: The function to trace
        show_args: Whether to show function arguments in the trace
        use_colors: Whether to use colors in the output
        colors: Custom color scheme dictionary
        show_time: Whether to show execution time (default: False)
    
    Returns:
        The wrapped function
    """
    # Use provided colors or defaults
    color_scheme = colors or DEFAULT_COLORS
    
    def decorator(f: F) -> F:
        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            depth = _get_call_depth()
            indent = _colorize("│   " * depth, color_scheme.get("tree", DEFAULT_COLORS["tree"]), use_colors)
            
            # Call the function and measure time
            _increment_depth()
            start_time = time.perf_counter()
            try:
                result = f(*args, **kwargs)
                end_time = time.perf_counter()
                execution_time = end_time - start_time
                _decrement_depth()
                
                # Handle generator functions
                if inspect.isgeneratorfunction(f):
                    def traced_generator():
                        try:
                            for value in result:
                                # Measure time for each yield
                                yield_start_time = time.perf_counter()
                                yield_value = value
                                yield_end_time = time.perf_counter()
                                yield_execution_time = yield_end_time - yield_start_time

                                # Add node to trace graph for each yielded value
                                _trace_graph.add_node(
                                    function_name=f"{f.__name__} (yield)",
                                    args=_get_args_dict((f,) + args, kwargs) if show_args else {},
                                    return_value=yield_value,
                                    execution_time=yield_execution_time,
                                    depth=depth
                                )
                                
                                # Print yield value with time
                                yields = _colorize("yields: ", color_scheme.get("returns", DEFAULT_COLORS["returns"]), use_colors)
                                value_str = _colorize(f"{yield_value!r}", color_scheme.get("returns", DEFAULT_COLORS["returns"]), use_colors)
                                
                                if show_time:
                                    time_str = _format_time(yield_execution_time)
                                    time_color = _get_time_color(yield_execution_time, color_scheme)
                                    time_str = _colorize(f"took {time_str}", time_color, use_colors, bold=True)
                                    print(f"{indent}├── {yields}{value_str} --> {time_str}")
                                else:
                                    print(f"{indent}├── {yields}{value_str}")
                                
                                yield yield_value
                            
                            # Add final node for generator completion
                            completion_time = time.perf_counter() - start_time
                            _trace_graph.add_node(
                                function_name=f"{f.__name__} (complete)",
                                args=_get_args_dict((f,) + args, kwargs) if show_args else {},
                                return_value="Generator completed",
                                execution_time=completion_time,
                                depth=depth
                            )
                            
                            # Print completion message with time
                            complete = _colorize("generator complete", color_scheme.get("returns", DEFAULT_COLORS["returns"]), use_colors)
                            
                            if show_time:
                                time_str = _format_time(completion_time)
                                time_color = _get_time_color(completion_time, color_scheme)
                                time_str = _colorize(f"took {time_str}", time_color, use_colors, bold=True)
                                print(f"{indent}└── {complete} --> {time_str}")
                            else:
                                print(f"{indent}└── {complete}")
                            
                        except Exception as e:
                            # Add error node for generator
                            error_time = time.perf_counter() - start_time
                            _trace_graph.add_node(
                                function_name=f"{f.__name__} (error)",
                                args=_get_args_dict((f,) + args, kwargs) if show_args else {},
                                return_value=f"{type(e).__name__}: {str(e)}",
                                execution_time=error_time,
                                depth=depth
                            )
                            
                            error = _colorize("generator raises: ", color_scheme.get("error", DEFAULT_COLORS["error"]), use_colors)
                            error_type = _colorize(f"{type(e).__name__}", color_scheme.get("error", DEFAULT_COLORS["error"]), use_colors)
                            error_msg = _colorize(f": {str(e)}", color_scheme.get("error", DEFAULT_COLORS["error"]), use_colors)
                            
                            if show_time:
                                time_str = _format_time(error_time)
                                time_color = _get_time_color(error_time, color_scheme)
                                time_str = _colorize(f"took {time_str}", time_color, use_colors, bold=True)
                                print(f"{indent}└── {error}{error_type}{error_msg} --> {time_str}")
                            else:
                                print(f"{indent}└── {error}{error_type}{error_msg}")
                            
                            raise
                    
                    return traced_generator()
                
                # Add node to trace graph for regular functions
                _trace_graph.add_node(
                    function_name=f.__name__,
                    args=_get_args_dict((f,) + args, kwargs) if show_args else {},
                    return_value=result,
                    execution_time=execution_time,
                    depth=depth
                )
                
                # Format function call with time
                if show_args:
                    arg_str = _format_args((f,) + args, kwargs)
                    func_name = _colorize(f.__name__, color_scheme.get("function", DEFAULT_COLORS["function"]), use_colors)
                    args_str = _colorize(f"({arg_str})", color_scheme.get("args", DEFAULT_COLORS["args"]), use_colors)
                    
                    if show_time:
                        time_str = _format_time(execution_time)
                        time_color = _get_time_color(execution_time, color_scheme)
                        time_str = _colorize(f"took {time_str}", time_color, use_colors, bold=True)
                        print(f"{indent}├── {func_name}{args_str} --> {time_str}")
                    else:
                        print(f"{indent}├── {func_name}{args_str}")
                else:
                    func_name = _colorize(f.__name__, color_scheme.get("function", DEFAULT_COLORS["function"]), use_colors)
                    
                    if show_time:
                        time_str = _format_time(execution_time)
                        time_color = _get_time_color(execution_time, color_scheme)
                        time_str = _colorize(f"took {time_str}", time_color, use_colors, bold=True)
                        print(f"{indent}├── {func_name}() --> {time_str}")
                    else:
                        print(f"{indent}├── {func_name}()")
                
                # Print return value
                returns = _colorize("returns: ", color_scheme.get("returns", DEFAULT_COLORS["returns"]), use_colors)
                result_str = _colorize(f"{result!r}", color_scheme.get("returns", DEFAULT_COLORS["returns"]), use_colors)
                print(f"{indent}└── {returns}{result_str}")
                
                return result
            except Exception as e:
                end_time = time.perf_counter()
                execution_time = end_time - start_time
                _decrement_depth()
                
                # Add error node to trace graph
                _trace_graph.add_node(
                    function_name=f.__name__,
                    args=_get_args_dict((f,) + args, kwargs) if show_args else {},
                    return_value=f"{type(e).__name__}: {str(e)}",
                    execution_time=execution_time,
                    depth=depth
                )
                
                # Format function call with time
                if show_args:
                    arg_str = _format_args((f,) + args, kwargs)
                    func_name = _colorize(f.__name__, color_scheme.get("function", DEFAULT_COLORS["function"]), use_colors)
                    args_str = _colorize(f"({arg_str})", color_scheme.get("args", DEFAULT_COLORS["args"]), use_colors)
                    
                    if show_time:
                        time_str = _format_time(execution_time)
                        time_color = _get_time_color(execution_time, color_scheme)
                        time_str = _colorize(f"took {time_str}", time_color, use_colors, bold=True)
                        print(f"{indent}├── {func_name}{args_str} --> {time_str}")
                    else:
                        print(f"{indent}├── {func_name}{args_str}")
                else:
                    func_name = _colorize(f.__name__, color_scheme.get("function", DEFAULT_COLORS["function"]), use_colors)
                    
                    if show_time:
                        time_str = _format_time(execution_time)
                        time_color = _get_time_color(execution_time, color_scheme)
                        time_str = _colorize(f"took {time_str}", time_color, use_colors, bold=True)
                        print(f"{indent}├── {func_name}() --> {time_str}")
                    else:
                        print(f"{indent}├── {func_name}()")
                
                error = _colorize("raises: ", color_scheme.get("error", DEFAULT_COLORS["error"]), use_colors)
                error_type = _colorize(f"{type(e).__name__}", color_scheme.get("error", DEFAULT_COLORS["error"]), use_colors)
                error_msg = _colorize(f": {str(e)}", color_scheme.get("error", DEFAULT_COLORS["error"]), use_colors)
                print(f"{indent}└── {error}{error_type}{error_msg}")
                
                raise
        
        return wrapper
    
    if func is None:
        return decorator
    return decorator(func)

def save_trace(filename: str, format: str = "png", title: str = "Function Call Trace") -> None:
    """
    Save the current trace as a graph file.
    
    Args:
        filename: Output filename (without extension)
        format: Output format ("dot" or "png")
        title: Graph title
    """
    if format == "dot":
        _trace_graph.save_dot(f"{filename}.dot", title)
    elif format == "png":
        _trace_graph.save_png(filename, title)
    else:
        raise ValueError("Format must be 'dot' or 'png'")

def trace_module(module, show_args: bool = True, use_colors: bool = True, 
                colors: Optional[Dict[str, str]] = None, show_time: bool = False) -> None:
    """
    Trace all functions in a module.
    
    Args:
        module: The module to trace
        show_args: Whether to show function arguments in the trace
        use_colors: Whether to use colors in the output
        colors: Custom color scheme dictionary
        show_time: Whether to show execution time
    """
    # Handle both module and class objects
    if isinstance(module, type):
        # For classes, we need to handle both static methods and instance methods
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj):
                # Handle static methods
                if isinstance(obj, staticmethod):
                    setattr(module, name, staticmethod(trace(
                        show_args=show_args,
                        use_colors=use_colors,
                        colors=colors,
                        show_time=show_time
                    )(obj.__func__)))
                # Handle regular methods
                elif not name.startswith('__'):
                    setattr(module, name, trace(
                        show_args=show_args,
                        use_colors=use_colors,
                        colors=colors,
                        show_time=show_time
                    )(obj))
    else:
        # For regular modules
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) and obj.__module__ == module.__name__:
                setattr(module, name, trace(
                    show_args=show_args,
                    use_colors=use_colors,
                    colors=colors,
                    show_time=show_time
                )(obj)) 