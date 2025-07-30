# Tracegraph

[![PyPI version](https://badge.fury.io/py/tracegraph.svg)](https://badge.fury.io/py/tracegraph)
[![Python Versions](https://img.shields.io/pypi/pyversions/tracegraph.svg)](https://pypi.org/project/tracegraph/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Tracegraph is a zero-dependency Python library that allows developers to trace, visualize, and understand function calls and their return values. It provides a simple way to see the call hierarchy and flow of your Python code through terminal-based output.

## Features

- 🎯 Simple `@trace` decorator for function tracing
- 🌳 Beautiful tree-like visualization of function calls
- 🎨 Color-coded output with customizable colors
- ⏱️ Execution time tracking with color-coded timing
- 🔄 Thread-safe depth tracking
- 📝 Automatic argument formatting
- 🚀 No external dependencies
- 📊 Graph export to DOT/PNG format

## Installation

```bash
pip install tracegraph
```

For Graphviz export support (optional):
```bash
pip install tracegraph[graphviz]
```

## Quick Start

```python
from tracegraph import trace

@trace
def calculate_tax(income):
    return income * 0.3

@trace
def calculate_net_income(income):
    return income - calculate_tax(income)

# Call the function
result = calculate_net_income(100000)
```

Output:
```
├── calculate_net_income(income=100000) --> took 0.15 milliseconds
│   ├── calculate_tax(income=100000) --> took 0.05 milliseconds
│   └── returns: 30000.0
└── returns: 70000.0
```

## Usage

### Basic Usage

Simply add the `@trace` decorator to any function you want to trace:

```python
from tracegraph import trace

@trace
def my_function(x, y):
    return x + y
```

### Hiding Arguments

If you want to hide the function arguments in the trace:

```python
@trace(show_args=False)
def my_function(x, y):
    return x + y
```

### Color Options

By default, Tracegraph uses color-coded output. You can customize the colors or disable them:

```python
from tracegraph import trace, Colors

# Disable colors
@trace(use_colors=False)
def no_colors(x):
    return x * 2

# Custom colors
custom_colors = {
    "function": Colors.RED,    # Function names
    "args": Colors.YELLOW,     # Arguments
    "returns": Colors.MAGENTA, # Return values
    "error": Colors.BLUE,      # Error messages
    "tree": Colors.WHITE,      # Tree structure
}

@trace(colors=custom_colors)
def custom_colors(x):
    return x * 2
```

#### Supported Colors

Tracegraph supports the following ANSI colors:

| Color    | Code           | Description                    |
|----------|----------------|--------------------------------|
| `RED`    | `\033[31m`     | Red text                       |
| `GREEN`  | `\033[32m`     | Green text                     |
| `YELLOW` | `\033[33m`     | Yellow text                    |
| `BLUE`   | `\033[34m`     | Blue text                      |
| `MAGENTA`| `\033[35m`     | Magenta text                   |
| `CYAN`   | `\033[36m`     | Cyan text                      |
| `WHITE`  | `\033[37m`     | White text                     |
| `BOLD`   | `\033[1m`      | Bold text (can be combined)    |
| `RESET`  | `\033[0m`      | Reset to default color         |

Default color scheme:
- Function names: `CYAN`
- Arguments: `WHITE`
- Return values: `GREEN`
- Error messages: `RED`
- Tree structure: `BLUE`
- Time (fast): `GREEN` (≤ 1s)
- Time (medium): `YELLOW` (1s - 5s)
- Time (slow): `RED` (> 5s)

You can combine colors with `BOLD` for emphasis:
```python
custom_colors = {
    "function": Colors.BOLD + Colors.RED,  # Bold red function names
    "returns": Colors.BOLD + Colors.GREEN, # Bold green return values
    # ... other colors ...
}
```

### Execution Time

Tracegraph automatically measures and displays execution time for each function call. The time is color-coded based on duration:

```python
from tracegraph import trace
import time

@trace
def fast_function():
    return "fast"  # Will show in green (≤ 1s)

@trace
def medium_function():
    time.sleep(3)  # Will show in yellow (1s - 5s)
    return "medium"

@trace
def slow_function():
    time.sleep(6)  # Will show in red (> 5s)
    return "slow"
```

Time units are automatically chosen based on duration:
- Microseconds (µs) for very fast operations
- Milliseconds (ms) for operations under 1 second
- Seconds (s) for operations under 1 minute
- Minutes (min) for operations under 1 hour
- Hours (hr) for very long operations

You can disable time display:
```python
@trace(show_time=False)
def no_time(x):
    return x * 2
```

### Graph Export

Tracegraph can export function call traces as graphs in DOT or PNG format:

```python
from tracegraph import trace, save_trace

@trace
def process_data(data):
    return data * 2

@trace
def analyze_data(data):
    result = process_data(data)
    return result + 1

# Run some functions
result = analyze_data(5)

# Save the trace as a graph
save_trace("trace", format="png", title="Data Processing Trace")
```

This will create a `trace.png` file showing the function call hierarchy with:
- Color-coded nodes based on execution time
- Function arguments and return values
- Execution time for each function
- Clear visualization of the call hierarchy

The graph will use the same color scheme as the terminal output:
- Green for fast functions (≤ 1s)
- Yellow for medium functions (1s - 5s)
- Red for slow functions (> 5s)

You can also save the trace as a DOT file for further customization:
```python
save_trace("trace", format="dot")
```

Note: PNG export requires Graphviz to be installed. Install it with:
```bash
pip install tracegraph[graphviz]
```

## Module Tracing

Tracegraph can also trace all functions in a module at once using the `trace_module` function:

```python
from tracegraph import trace_module

# Create a module with multiple functions
class MathModule:
    def add(a, b):
        return a + b

    def multiply(x, y):
        return x * y

    def complex_operation(n):
        result = MathModule.add(n, 1)
        return MathModule.multiply(result, 2)

# Trace all functions in the module
trace_module(MathModule)

# Use the traced functions
result = MathModule.complex_operation(5)  # Will show nested function calls
```

The `trace_module` function supports all the same options as the `trace` decorator:

```python
# Trace with custom options
trace_module(
    your_module,
    show_args=True,      # Show function arguments (default: True)
    use_colors=True,     # Enable colored output (default: True)
    show_time=True,      # Show execution time (default: False)
    colors=custom_colors # Custom color scheme
)
```

This is particularly useful when you want to trace all functions in a module without decorating each one individually. The module tracing will show the call hierarchy between functions in the same module, making it easy to understand the flow of execution.

## Roadmap

- [x] Color-coded terminal output
- [x] Show execution time
- [x] Export to Graphviz `.dot` / PNG
- [x] Trace all functions in a module
- [x] Add support for tracing generator functions

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

- Abdul Rafey (abdulrafey38@gmail.com)
- Data Engineer at edX/Arbisoft

## Planned Features

### Performance Improvements
- [ ] Optimize memory usage for large traces
- [ ] Add async/await support for tracing coroutines
- [ ] Add support for concurrent tracing in multi-threaded applications

### Enhanced Visualization
- [ ] Add support for custom tree characters/styles
- [ ] Add support for different output formats (ASCII, Unicode, etc.)
- [ ] Add support for custom indentation levels

### Advanced Features
- [ ] Add support for tracing class methods and properties
- [ ] Add support for tracing context managers (with statements)

### Generator Functions

Tracegraph supports tracing generator functions, showing each yielded value and generator completion:

```python
from tracegraph import trace

@trace
def fibonacci(n):
    """Generate Fibonacci numbers up to n."""
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

# Use the generator
for num in fibonacci(5):
    print(f"Got Fibonacci number: {num}")
```

Output:
```
├── fibonacci(n=5)
├── yields: 0
├── yields: 1
├── yields: 1
├── yields: 2
├── yields: 3
└── generator complete
```

The trace shows:
- Each yielded value
- Generator completion
- Any errors that occur during generation
- Execution time for each yield (if enabled)
