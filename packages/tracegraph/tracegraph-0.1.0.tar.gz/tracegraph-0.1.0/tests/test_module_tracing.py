"""
Tests for module tracing functionality.
"""

import unittest
from io import StringIO
import sys
import time
from tracegraph import trace_module, Colors

class TestModuleTracing(unittest.TestCase):
    def setUp(self):
        self.output = StringIO()
        self.original_stdout = sys.stdout
        sys.stdout = self.output

    def tearDown(self):
        sys.stdout = self.original_stdout

    def test_module_tracing(self):
        # Create a test module with multiple functions
        class TestModule:
            def add(a, b):
                return a + b

            def multiply(x, y):
                return x * y

            def complex_operation(n):
                result = TestModule.add(n, 1)
                return TestModule.multiply(result, 2)

        # Trace all functions in the module
        trace_module(TestModule)

        # Test the traced functions
        result = TestModule.complex_operation(5)
        self.assertEqual(result, 12)  # (5 + 1) * 2 = 12

        output = self.output.getvalue()
        # Check that all function calls are traced
        self.assertIn("complex_operation", output)
        self.assertIn("add", output)
        self.assertIn("multiply", output)
        self.assertIn("n=5", output)
        self.assertIn(Colors.GREEN, output)  # Color for returns
        self.assertIn("12", output)  # Final return value

    def test_module_tracing_with_time(self):
        class TestModule:
            def fast_func():
                return "fast"

            def slow_func():
                time.sleep(0.1)
                return "slow"

        # Trace all functions with time enabled
        trace_module(TestModule, show_time=True)

        # Test the traced functions
        TestModule.fast_func()
        TestModule.slow_func()

        output = self.output.getvalue()
        # Check that time is shown for both functions
        self.assertIn("took", output)
        self.assertIn("fast_func", output)
        self.assertIn("slow_func", output)
        self.assertIn(Colors.GREEN, output)  # Color for returns
        self.assertIn("fast", output)  # Return value
        self.assertIn("slow", output)  # Return value

    def test_module_tracing_with_custom_colors(self):
        class TestModule:
            def test_func(x):
                return x * 2

        # Define custom colors
        custom_colors = {
            "function": Colors.RED,
            "args": Colors.YELLOW,
            "returns": Colors.MAGENTA,
            "error": Colors.BLUE,
            "tree": Colors.WHITE,
        }

        # Trace with custom colors
        trace_module(TestModule, colors=custom_colors)

        # Test the traced function
        result = TestModule.test_func(5)
        self.assertEqual(result, 10)

        output = self.output.getvalue()
        # Check for custom colors
        self.assertIn(Colors.RED, output)  # Function name
        self.assertIn(Colors.YELLOW, output)  # Arguments
        self.assertIn(Colors.MAGENTA, output)  # Return value
        self.assertIn(Colors.WHITE, output)  # Tree structure
        self.assertIn("test_func", output)
        self.assertIn("x=5", output)
        self.assertIn("10", output)  # Return value

if __name__ == '__main__':
    unittest.main() 