"""
Tests for the tracegraph tracer functionality.
"""

import unittest
from io import StringIO
import sys
import time
from tracegraph import trace, Colors

class TestTracer(unittest.TestCase):
    def setUp(self):
        self.output = StringIO()
        self.original_stdout = sys.stdout
        sys.stdout = self.output

    def tearDown(self):
        sys.stdout = self.original_stdout

    def test_basic_tracing(self):
        @trace
        def add(a, b):
            return a + b

        result = add(1, 2)
        self.assertEqual(result, 3)
        output = self.output.getvalue()
        self.assertIn("add", output)
        self.assertIn("a=1, b=2", output)
        self.assertIn(Colors.GREEN, output)  # Color for returns
        self.assertIn("3", output)  # Return value
        # Time should not be shown by default
        self.assertNotIn("took", output)

    def test_nested_tracing(self):
        @trace
        def inner(x):
            return x * 2

        @trace
        def outer(x):
            return inner(x) + 1

        result = outer(5)
        self.assertEqual(result, 11)
        output = self.output.getvalue()
        self.assertIn("outer", output)
        self.assertIn("inner", output)
        self.assertIn("x=5", output)
        self.assertIn(Colors.GREEN, output)  # Color for returns
        self.assertIn("10", output)  # Inner return value
        self.assertIn("11", output)  # Outer return value
        # Time should not be shown by default
        self.assertNotIn("took", output)

    def test_hide_args(self):
        @trace(show_args=False)
        def secret(x, y):
            return x + y

        result = secret(1, 2)
        self.assertEqual(result, 3)
        output = self.output.getvalue()
        self.assertIn("secret", output)
        self.assertNotIn("x=1", output)
        self.assertNotIn("y=2", output)
        self.assertIn(Colors.GREEN, output)  # Color for returns
        self.assertIn("3", output)  # Return value
        # Time should not be shown by default
        self.assertNotIn("took", output)

    def test_exception_tracing(self):
        @trace
        def raise_error():
            raise ValueError("test error")

        with self.assertRaises(ValueError):
            raise_error()
        
        output = self.output.getvalue()
        self.assertIn("raise_error", output)
        self.assertIn(Colors.RED, output)  # Color for error
        self.assertIn("ValueError", output)
        self.assertIn("test error", output)
        # Time should not be shown by default
        self.assertNotIn("took", output)

    def test_colors_enabled(self):
        @trace(use_colors=True)
        def colored_func(x):
            return x * 2

        result = colored_func(5)
        self.assertEqual(result, 10)
        output = self.output.getvalue()
        # Check for ANSI color codes
        self.assertIn(Colors.CYAN, output)  # Function name
        self.assertIn(Colors.GREEN, output)  # Return value
        self.assertIn(Colors.RESET, output)  # Reset code
        # Time should not be shown by default
        self.assertNotIn("took", output)

    def test_colors_disabled(self):
        @trace(use_colors=False)
        def uncolored_func(x):
            return x * 2

        result = uncolored_func(5)
        self.assertEqual(result, 10)
        output = self.output.getvalue()
        # Check that no ANSI codes are present
        self.assertNotIn(Colors.CYAN, output)
        self.assertNotIn(Colors.GREEN, output)
        self.assertNotIn(Colors.RESET, output)
        # Time should not be shown by default
        self.assertNotIn("took", output)

    def test_custom_colors(self):
        custom_colors = {
            "function": Colors.RED,
            "args": Colors.YELLOW,
            "returns": Colors.MAGENTA,
            "error": Colors.BLUE,
            "tree": Colors.WHITE,
        }

        @trace(colors=custom_colors)
        def custom_colored_func(x):
            return x * 2

        result = custom_colored_func(5)
        self.assertEqual(result, 10)
        output = self.output.getvalue()
        # Check for custom colors
        self.assertIn(Colors.RED, output)  # Function name
        self.assertIn(Colors.YELLOW, output)  # Arguments
        self.assertIn(Colors.MAGENTA, output)  # Return value
        self.assertIn(Colors.WHITE, output)  # Tree structure
        self.assertIn("10", output)  # Return value

    def test_execution_time_fast(self):
        @trace(show_time=True)
        def fast_func():
            return "fast"

        result = fast_func()
        self.assertEqual(result, "fast")
        output = self.output.getvalue()
        # Check for time output with green color (fast)
        self.assertIn("took", output)
        self.assertIn("microseconds", output)  # Should be microseconds
        self.assertIn("fast", output)  # Return value

    def test_execution_time_medium(self):
        @trace(show_time=True)
        def medium_func():
            time.sleep(0.2)  # 200ms
            return "medium"

        result = medium_func()
        self.assertEqual(result, "medium")
        output = self.output.getvalue()
        # Check for time output with yellow color (medium)
        self.assertIn("took", output)
        self.assertIn("milliseconds", output)  # Should be milliseconds
        self.assertIn("medium", output)  # Return value

    def test_execution_time_slow(self):
        @trace(show_time=True)
        def slow_func():
            time.sleep(1.1)  # 1.1s
            return "slow"

        result = slow_func()
        self.assertEqual(result, "slow")
        output = self.output.getvalue()
        # Check for time output with red color (slow)
        self.assertIn("took", output)
        self.assertIn("seconds", output)  # Should be seconds
        self.assertIn("slow", output)  # Return value

    def test_hide_execution_time(self):
        @trace(show_time=False)
        def func():
            time.sleep(0.1)
            return "no time shown"

        result = func()
        self.assertEqual(result, "no time shown")
        output = self.output.getvalue()
        # Check that no time output is present
        self.assertNotIn("took", output)
        self.assertNotIn("milliseconds", output)
        self.assertNotIn("seconds", output)
        self.assertIn("no time shown", output)  # Return value

if __name__ == '__main__':
    unittest.main() 