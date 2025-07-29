"""
Yamlify Package - Software Detailed Design

This package provides functionality for converting YAML files to rendered output
using Jinja2 templates. It serves as a tool for generating documents from YAML data.

The package is organized into several modules:
- convert: Main conversion functionality
- yaml_loader: YAML file loading
- template_renderer: Template rendering
- utils: Utility functions
- data: Data processing (legacy)
- main: Command-line interface

Public API:
- Main Functions:
  - convert: Main function for converting YAML files to rendered output
  - main: Entry point for the command-line interface

- YAML Loading:
  - read_folder: Function for reading YAML files from a directory
  - load_yaml_files: Function for loading YAML files from a directory (non-recursive)
  - load_yaml_files_recursively: Function for loading YAML files recursively from a directory

- Template Rendering:
  - render_template: Function for rendering a Jinja2 template with data
  - markdown_to_html: Filter for converting markdown text to HTML
  - to_json: Filter for converting data to JSON

- Utilities:
  - show_structure: Function for displaying the structure of a dictionary
"""

__version__ = "0.2.1"

from .main import main
from .convert import convert
from .data import read_folder
from .yaml_loader import load_yaml_files, load_yaml_files_recursively
from .template_renderer import render_template, markdown_to_html, to_json
from .utils import show_structure
