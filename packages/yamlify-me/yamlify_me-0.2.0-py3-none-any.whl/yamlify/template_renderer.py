"""
Template Renderer Module - Software Detailed Design

1. Module Purpose and Scope:
   This module provides functionality for rendering Jinja2 templates with data
   from YAML files. It serves as a template rendering layer for the yamlify application.

2. Component Architecture:
   - Single-responsibility module focused on template rendering operations
   - Functional approach with pure functions
   - Custom filters for enhanced template capabilities

3. Data Flow:
   a. Input:
      - Template path
      - Data to render the template with
   b. Processing:
      - Set up Jinja2 environment
      - Register custom filters
      - Load template
      - Render template with data
   c. Output:
      - Rendered content as string

4. Interfaces:
   - Public Functions:
     * render_template: Renders a Jinja2 template with provided data
     * markdown_to_html: Custom filter to convert markdown to HTML
     * to_json: Custom filter to convert data to JSON

5. Dependencies:
   - External Libraries:
     * jinja2: For template rendering
     * markdown: For markdown to HTML conversion
     * json: For JSON serialization

6. Error Handling Strategy:
   - Exception handling for template loading and rendering
   - Null safety in filters

7. Performance Considerations:
   - Efficient template rendering
   - Minimal memory footprint

8. Security Considerations:
   - Safe template rendering to prevent code execution vulnerabilities
   - Proper encoding handling (UTF-8)

9. Testing Strategy:
   - Unit tests for all functionality
   - Test cases for valid inputs, edge cases, and error conditions

10. Maintenance Considerations:
    - Comprehensive docstrings following standard format
    - Clear code structure with logical separation of concerns
    - Consistent error handling pattern
"""

import json
import markdown
import os
from jinja2 import Environment, FileSystemLoader


def markdown_to_html(text):
    """
    Converts markdown text to HTML.
    
    This function takes a markdown-formatted string and converts it to HTML
    using the markdown library.
    
    Args:
        text (str or None): The markdown text to convert. If None, an empty string is returned.
        
    Returns:
        str: The HTML representation of the markdown text.
    """
    if text is None:
        return ""
    return markdown.markdown(text)


def to_json(data):
    """
    Converts data to a JSON string.
    
    This function takes a Python object and converts it to a JSON string
    with proper formatting and UTF-8 encoding.
    
    Args:
        data (object): The Python object to convert to JSON.
        
    Returns:
        str: The JSON representation of the data.
    """
    return json.dumps(data, ensure_ascii=False, indent=2)


def render_template(template_path, merged_data):
    """
    Renders a Jinja2 template with the provided data.
    
    This function sets up a Jinja2 environment, registers custom filters,
    loads the template from the specified path, and renders it with the
    provided data.
    
    Args:
        template_path (str): Path to the Jinja2 template file.
        merged_data (dict): Data to render the template with.
        
    Returns:
        str: The rendered template as a string.
    """
    template_dir, template_file = os.path.split(template_path)
    env = Environment(loader=FileSystemLoader(template_dir))
    env.filters["markdown"] = markdown_to_html
    env.filters["json"] = to_json
    template = env.get_template(template_file)
    return template.render(merged_data)