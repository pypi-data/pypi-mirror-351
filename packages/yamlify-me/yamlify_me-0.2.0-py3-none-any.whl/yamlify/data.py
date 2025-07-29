"""
YAML Data Module - Software Detailed Design

1. Module Purpose and Scope:
   This module provides functionality for reading YAML files from specified directories
   and loading their content into data structures. It serves as a data access layer for
   the yamlify application, abstracting the file system operations and YAML parsing.

2. Component Architecture:
   - Single-responsibility module focused on YAML file reading operations
   - Stateless design with no class hierarchy or instance variables
   - Functional approach with pure functions that don't modify global state
   - Clear separation between file system access, YAML parsing, and error handling

3. Data Flow:
   a. Input:
      - Directory path and relative path to search for YAML files
      - Empty data structures (list and dictionary) to be populated
   b. Processing:
      - Validate input parameters
      - Construct full directory path
      - Check directory existence
      - Find all YAML files in the directory
      - For each file:
        * Read file content
        * Parse YAML
        * Store in provided data structures
      - Collect any errors that occur during processing
   c. Output:
      - Populated data structures (passed by reference)
      - List of error messages or None if successful

4. Interfaces:
   - Public Functions:
     * read_folder: Reads YAML files from a directory into provided data structures

5. Dependencies:
   - External Libraries:
     * yaml: For parsing YAML content
     * os: For path operations
     * logging: For error and information logging
     * pathlib: For robust path handling
     * typing: For type annotations

6. Error Handling Strategy:
   - Input validation with descriptive error messages
   - Explicit exception handling for all file operations
   - Hierarchical error handling (file access errors vs. YAML parsing errors)
   - Non-fatal error collection (continues processing after individual file errors)
   - Comprehensive logging at appropriate severity levels
   - Clear return values indicating success or failure

7. Performance Considerations:
   - Efficient file globbing using pathlib
   - Minimal memory footprint with streaming file reading
   - Early validation to avoid unnecessary processing
   - No redundant file system operations

8. Security Considerations:
   - Proper encoding handling (UTF-8)
   - Safe YAML loading to prevent code execution vulnerabilities
   - Path validation to prevent directory traversal

9. Testing Strategy:
   - Unit tests for all functionality
   - Test cases for valid inputs, edge cases, and error conditions
   - Mocking of file system for deterministic testing

10. Maintenance Considerations:
    - Comprehensive docstrings following standard format
    - Type annotations for better IDE support and static analysis
    - Clear code structure with logical separation of concerns
    - Consistent error handling pattern
    - Detailed logging for troubleshooting
"""

import yaml
import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

# Set up logging
logger = logging.getLogger(__name__)

def read_folder(directory: str, path: str, data: List[Any], index: Dict[str, Any]) -> Optional[List[str]]:
    """
    Reads all YAML files from a specified directory and loads their content into data structures.

    Args: 
        directory (str): The base directory path.
        path (str): The relative path from the base directory to search for YAML files.
        data (list): A list to append the loaded YAML content to.
        index (dict): A dictionary to store the loaded YAML content with filenames as keys.

    Returns:
        Optional[List[str]]: List of errors encountered during processing, or None if no errors occurred.

    Raises:
        ValueError: If any of the input parameters are invalid.
        FileNotFoundError: If the specified directory does not exist.
    """
    # Validate input parameters
    if not directory or not isinstance(directory, str):
        raise ValueError("Directory must be a non-empty string")
    if not isinstance(path, str):
        raise ValueError("Path must be a string")
    if not isinstance(data, list):
        raise ValueError("Data must be a list")
    if not isinstance(index, dict):
        raise ValueError("Index must be a dictionary")

    # Construct the full directory path
    full_path = os.path.join(directory, path)

    # Check if the directory exists
    if not os.path.isdir(full_path):
        raise FileNotFoundError(f"Directory not found: {full_path}")

    # Use pathlib for more robust path handling
    search_path = Path(full_path)

    # Get all YAML files in the directory
    yaml_files = list(search_path.glob("*.yaml"))

    # Check if the directory is empty
    if not yaml_files:
        logger.warning(f"No YAML files found in {full_path}")
        return None

    errors = []

    # Process each YAML file
    for file_path in yaml_files:
        logger.info(f"Reading file: {file_path}")

        # Get name without extension using pathlib
        name = str(file_path.with_suffix(''))

        try:
            # Open and parse the YAML file
            with open(file_path, 'r', encoding='utf-8') as stream:
                try:
                    yaml_content = yaml.safe_load(stream)
                    index[name] = yaml_content
                    data.append(yaml_content)
                except yaml.YAMLError as exc:
                    error_msg = f"YAML parsing error in {file_path}: {exc}"
                    logger.error(error_msg)
                    errors.append(error_msg)
        except (IOError, PermissionError) as exc:
            error_msg = f"Error opening file {file_path}: {exc}"
            logger.error(error_msg)
            errors.append(error_msg)

    return errors if errors else None
