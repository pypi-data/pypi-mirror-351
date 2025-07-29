import unittest
import sys
import os
import tempfile
import json

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from yamlify.template_renderer import markdown_to_html, to_json, render_template


class TestTemplateRenderer(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test templates
        self.temp_dir = tempfile.mkdtemp()

        # Create test templates
        self.create_test_templates()

    def tearDown(self):
        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.temp_dir)

    def create_test_templates(self):
        # Create a simple template
        simple_template = "Hello, {{ name }}!"
        with open(os.path.join(self.temp_dir, "simple.j2"), "w") as f:
            f.write(simple_template)

        # Create a template with filters
        filter_template = """
        # {{ title }}

        {{ description | markdown }}

        {{ data | json }}
        """
        with open(os.path.join(self.temp_dir, "filter.j2"), "w") as f:
            f.write(filter_template)

        # Create a template with loops
        loop_template = """
        {% for item in items %}
        - {{ item.name }}: {{ item.value }}
        {% endfor %}
        """
        with open(os.path.join(self.temp_dir, "loop.j2"), "w") as f:
            f.write(loop_template)

    def test_markdown_to_html(self):
        """Test converting markdown to HTML."""
        # Test with a simple markdown string
        markdown_text = "# Heading\n\nThis is a paragraph with **bold** text."
        html = markdown_to_html(markdown_text)

        # Check that the HTML contains the expected elements
        self.assertIn("<h1>Heading</h1>", html)
        self.assertIn("<strong>bold</strong>", html)

        # Test with None
        self.assertEqual(markdown_to_html(None), "")

    def test_to_json(self):
        """Test converting data to JSON."""
        # Test with a dictionary
        data = {"name": "John", "age": 30, "city": "New York"}
        json_str = to_json(data)

        # Check that the JSON string can be parsed back to the original data
        parsed_data = json.loads(json_str)
        self.assertEqual(parsed_data, data)

        # Test with a list
        data = [1, 2, 3, 4, 5]
        json_str = to_json(data)
        parsed_data = json.loads(json_str)
        self.assertEqual(parsed_data, data)

        # Test with nested structures
        data = {"people": [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]}
        json_str = to_json(data)
        parsed_data = json.loads(json_str)
        self.assertEqual(parsed_data, data)

    def test_render_template_simple(self):
        """Test rendering a simple template."""
        # Render the simple template
        template_path = os.path.join(self.temp_dir, "simple.j2")
        data = {"name": "World"}
        result = render_template(template_path, data)

        # Check the rendered result
        self.assertEqual(result, "Hello, World!")

    def test_render_template_with_filters(self):
        """Test rendering a template with filters."""
        # Render the filter template
        template_path = os.path.join(self.temp_dir, "filter.j2")
        data = {
            "title": "Test Title",
            "description": "This is a **test** description.",
            "data": {"key": "value"}
        }
        result = render_template(template_path, data)

        # Check the rendered result
        self.assertIn("# Test Title", result)  # Title is not processed by markdown filter
        self.assertIn("<strong>test</strong>", result)  # Description is processed by markdown filter
        self.assertIn('"key": "value"', result)  # Data is processed by json filter

    def test_render_template_with_loops(self):
        """Test rendering a template with loops."""
        # Render the loop template
        template_path = os.path.join(self.temp_dir, "loop.j2")
        data = {
            "items": [
                {"name": "Item 1", "value": "Value 1"},
                {"name": "Item 2", "value": "Value 2"},
                {"name": "Item 3", "value": "Value 3"}
            ]
        }
        result = render_template(template_path, data)

        # Check the rendered result
        self.assertIn("- Item 1: Value 1", result)
        self.assertIn("- Item 2: Value 2", result)
        self.assertIn("- Item 3: Value 3", result)


if __name__ == '__main__':
    unittest.main()
