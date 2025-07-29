import unittest
import sys
import os
import io
from contextlib import redirect_stdout

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from yamlify.utils import show_structure


class TestUtils(unittest.TestCase):
    def test_show_structure_simple_dict(self):
        """Test showing the structure of a simple dictionary."""
        # Create a simple dictionary
        data = {
            "name": "John",
            "age": 30,
            "city": "New York"
        }
        
        # Capture the output of show_structure
        output = io.StringIO()
        with redirect_stdout(output):
            show_structure(data)
        
        # Check the output
        output_str = output.getvalue()
        self.assertIn("name: str", output_str)
        self.assertIn("age: int", output_str)
        self.assertIn("city: str", output_str)

    def test_show_structure_nested_dict(self):
        """Test showing the structure of a nested dictionary."""
        # Create a nested dictionary
        data = {
            "person": {
                "name": "John",
                "age": 30,
                "address": {
                    "city": "New York",
                    "zip": "10001"
                }
            }
        }
        
        # Capture the output of show_structure
        output = io.StringIO()
        with redirect_stdout(output):
            show_structure(data)
        
        # Check the output
        output_str = output.getvalue()
        self.assertIn("person: dict", output_str)
        self.assertIn("  name: str", output_str)
        self.assertIn("  age: int", output_str)
        self.assertIn("  address: dict", output_str)
        self.assertIn("    city: str", output_str)
        self.assertIn("    zip: str", output_str)

    def test_show_structure_with_list(self):
        """Test showing the structure of a dictionary with a list of dictionaries."""
        # Create a dictionary with a list of dictionaries
        data = {
            "people": [
                {"name": "John", "age": 30},
                {"name": "Jane", "age": 25},
                {"name": "Bob", "age": 40}
            ]
        }
        
        # Capture the output of show_structure
        output = io.StringIO()
        with redirect_stdout(output):
            show_structure(data)
        
        # Check the output
        output_str = output.getvalue()
        self.assertIn("people: list", output_str)
        self.assertIn("  [3]", output_str)  # 3 items in the list
        self.assertIn("    name: str", output_str)
        self.assertIn("    age: int", output_str)

    def test_show_structure_empty_dict(self):
        """Test showing the structure of an empty dictionary."""
        # Create an empty dictionary
        data = {}
        
        # Capture the output of show_structure
        output = io.StringIO()
        with redirect_stdout(output):
            show_structure(data)
        
        # Check the output (should be empty)
        output_str = output.getvalue()
        self.assertEqual(output_str, "")

    def test_show_structure_complex_nested(self):
        """Test showing the structure of a complex nested dictionary."""
        # Create a complex nested dictionary
        data = {
            "company": {
                "name": "Example Corp",
                "founded": 2000,
                "departments": [
                    {
                        "name": "Engineering",
                        "employees": [
                            {"name": "John", "role": "Developer"},
                            {"name": "Jane", "role": "Manager"}
                        ]
                    },
                    {
                        "name": "Marketing",
                        "employees": [
                            {"name": "Bob", "role": "Specialist"}
                        ]
                    }
                ]
            }
        }
        
        # Capture the output of show_structure
        output = io.StringIO()
        with redirect_stdout(output):
            show_structure(data)
        
        # Check the output
        output_str = output.getvalue()
        self.assertIn("company: dict", output_str)
        self.assertIn("  name: str", output_str)
        self.assertIn("  founded: int", output_str)
        self.assertIn("  departments: list", output_str)
        self.assertIn("    name: str", output_str)
        self.assertIn("    employees: list", output_str)
        self.assertIn("      name: str", output_str)
        self.assertIn("      role: str", output_str)


if __name__ == '__main__':
    unittest.main()