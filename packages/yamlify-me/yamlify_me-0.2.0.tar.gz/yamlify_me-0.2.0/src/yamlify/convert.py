"""
Convert Module - Software Detailed Design

1. Module Purpose and Scope:
   This module provides the main conversion functionality for the yamlify application,
   orchestrating the process of loading YAML files, processing data, rendering templates,
   and generating output. It serves as the central coordinator that integrates the
   functionality from the specialized modules.

2. Component Architecture:
   - Orchestrator module that integrates functionality from other specialized modules
   - Functional approach with a main convert function
   - Clear separation of concerns with dependencies on specialized modules:
     * yaml_loader: Handles all YAML file loading operations
     * template_renderer: Manages template rendering
     * utils: Provides utility functions

3. Data Flow:
   a. Input:
      - Input directory containing YAML files
      - Template path
      - Output configuration (single file or multiple files)
      - Processing options (recursive loading, custom processor, etc.)
   b. Processing:
      - Load YAML files (recursive or non-recursive) using yaml_loader module
      - Process data with optional custom processor module
      - Optionally display the structure of the data using utils module
      - Render templates with data using template_renderer module
      - Generate output files or content
   c. Output:
      - List of dictionaries containing filenames and rendered content

4. Interfaces:
   - Public Functions:
     * convert: Main function that orchestrates the conversion process

5. Dependencies:
   - Internal Modules:
     * yaml_loader: For loading YAML files (load_yaml_files, load_yaml_files_recursively)
     * template_renderer: For rendering templates (render_template)
     * utils: For utility functions (show_structure)
   - External Libraries:
     * importlib: For dynamic module loading
     * sys: For path manipulation
     * os: For path operations

6. Error Handling Strategy:
   - Delegated to specialized modules for their specific operations
   - Informative error messages for orchestration issues
   - Proper handling of processor module loading and execution

7. Performance Considerations:
   - Efficient orchestration of operations
   - Minimal memory footprint
   - Optimal delegation to specialized modules

8. Security Considerations:
   - Safe module loading for custom processors
   - Delegated security concerns to specialized modules
   - Proper path handling

9. Testing Strategy:
   - Unit tests for the convert function
   - Integration tests for the entire conversion process
   - Tests for different configuration combinations

10. Maintenance Considerations:
    - Comprehensive docstrings following standard format
    - Clear code structure with logical separation of concerns
    - Consistent error handling pattern
    - Modular design for easy extension and modification
"""

import importlib
import sys
import os

# Import functions from other modules
from .yaml_loader import load_yaml_files, load_yaml_files_recursively
from .template_renderer import render_template
from .utils import show_structure


def convert(
    input_dir,
    template_path,
    output=None,
    output_filename_template=None,
    list_structure=False,
    processor=None,
    processor_path=None,
    recursive=False,
):
    """
    Convert YAML files to rendered output using Jinja2 templates.

    This function orchestrates the entire conversion process:
    1. Loads YAML files from the specified directory
    2. Optionally processes the data with a custom processor module
    3. Optionally displays the structure of the data
    4. Renders templates with the data
    5. Returns a list of dictionaries containing filenames and rendered content

    Args:
        input_dir (str): Path to the directory containing YAML files.
        template_path (str): Path to the Jinja2 template file.
        output (str, optional): Path to save the rendered document file.
            Only used if output_filename_template is None. Defaults to None.
        output_filename_template (str, optional): Template string for generating
            multiple output filenames, one for each input file. If provided,
            multiple output files will be generated. Defaults to None.
        list_structure (bool, optional): Whether to print the structure of the
            loaded data. Useful for debugging. Defaults to False.
        processor (str, optional): Name of a Python module with a process function
            to manipulate the loaded data before rendering. Defaults to None.
        processor_path (str, optional): Path to the directory containing the
            processor module. Defaults to None.
        recursive (bool, optional): Whether to load YAML files recursively from
            subdirectories. Defaults to False.

    Returns:
        list: A list of dictionaries, each containing:
            - 'filename': The output filename
            - 'content': The rendered content
    """
    # Load from each data file and merge data
    if recursive:
        merged_data = load_yaml_files_recursively(input_dir)
    else:
        merged_data = load_yaml_files(input_dir)

    # Check if the processor is specified
    if processor and processor_path:
        print("Loading processor module", processor)
        sys.path.append(os.path.abspath(processor_path))
        processor_module = importlib.import_module(processor)
        if hasattr(processor_module, "process"):
            print("Processing data")
            merged_data = processor_module.process(merged_data)
        else:
            print("The specified module does not have a 'filter_function'.")
    # Print structure
    if list_structure:
        show_structure(merged_data)
    # Initialize return data
    return_data = []
    # Check if multiple output files
    if output_filename_template:
        # Generate multiple output files based on the template
        for data in merged_data:
            # Generate filename
            filename = output_filename_template.format(**data)
            # Render data
            content = render_template(template_path, data)
            # Create putput structure
            return_data.append({"filename": filename, "content": content})
    else:
        # Render the Jinja2 template with the merged data
        content = render_template(template_path, {"data": merged_data})
        # Generate return data
        return_data.append({"filename": output, "content": content})
    # Return rendered data
    return return_data
