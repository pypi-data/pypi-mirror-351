"""
YAML Loader Module - Software Detailed Design

1. Module Purpose and Scope:
   This module provides functionality for loading YAML files from directories,
   both recursively and non-recursively. It serves as a data loading layer for
   the yamlify application.

2. Component Architecture:
   - Single-responsibility module focused on YAML file loading operations
   - Functional approach with pure functions
   - Clear separation between recursive and non-recursive loading

3. Data Flow:
   a. Input:
      - Directory path to search for YAML files
   b. Processing:
      - Check directory existence
      - Find all YAML files in the directory (and subdirectories if recursive)
      - For each file:
        * Read file content
        * Parse YAML
        * Add metadata to the parsed data
      - Collect any errors that occur during processing
   c. Output:
      - Structured data containing the parsed YAML content

4. Interfaces:
   - Public Functions:
     * load_yaml_files: Loads YAML files from a directory (non-recursive)
     * load_yaml_files_recursively: Loads YAML files recursively from a directory and its subdirectories

5. Dependencies:
   - External Libraries:
     * yaml: For parsing YAML content
     * os: For path operations
     * pathlib: For robust path handling

6. Error Handling Strategy:
   - Directory existence checking
   - Exception handling for file operations and YAML parsing
   - Informative error messages

7. Performance Considerations:
   - Efficient directory traversal
   - Minimal memory footprint with streaming file reading

8. Security Considerations:
   - Safe YAML loading to prevent code execution vulnerabilities
   - Proper encoding handling (UTF-8)

9. Testing Strategy:
   - Unit tests for all functionality
   - Test cases for valid inputs, edge cases, and error conditions

10. Maintenance Considerations:
    - Comprehensive docstrings following standard format
    - Clear code structure with logical separation of concerns
    - Consistent error handling pattern
"""

import yaml
import os
from pathlib import Path


def load_yaml_files_recursively(directory):
    """
    Recursively loads YAML files from a directory and its subdirectories.
    
    This function traverses the given directory and all its subdirectories,
    loading all YAML files (with .yaml or .yml extensions) it finds. The data
    from each file is loaded into a structured dictionary that preserves the
    directory hierarchy.
    
    Args:
        directory (str): Path to the directory containing YAML files.
        
    Returns:
        dict: A dictionary with the following structure:
            - 'elements': List of dictionaries, each containing the data from a YAML file
            - 'children': Dictionary mapping subdirectory names to their recursive results
            - 'directory': The original directory path
            - 'dirname': The name of the directory
            
    Raises:
        SystemExit: If the directory does not exist.
    """
    all_data = {
        "elements": [],
        "children": {},
        "directory": directory,
        "dirname": os.path.basename(directory),
    }

    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        exit(1)

    for filename in sorted(os.listdir(directory)):
        # For all yaml files
        filepath = os.path.join(directory, filename)
        if os.path.isdir(filepath):
            print("Entering directory: ", filepath)
            all_data["children"][filename] = load_yaml_files_recursively(filepath)
        elif filename.endswith(".yaml") or filename.endswith(".yml"):
            print("Reading file:", filepath)
            try:
                with open(filepath, "r", encoding="utf-8") as file:
                    data = yaml.safe_load(file) or {}  # Handle empty files
                    data.setdefault("filename", filename)
                    data.setdefault("filepath", filepath)
                    data.setdefault("directory", directory)
                    data.setdefault("group", filepath.split("/")[::-1])
                    data.setdefault("key", Path(filename).stem)
                    # Add data
                    all_data["elements"].append(data)
            except yaml.YAMLError as e:
                print(f"Error parsing {filename}: {e}")
            except Exception as e:
                print(f"Unexpected error with {filename}: {e}")
    # Return datasets
    return all_data


def load_yaml_files(directory):
    """
    Loads YAML files from a directory (non-recursive).
    
    This function reads all YAML files (with .yaml or .yml extensions) from the
    given directory and loads their content into a list of dictionaries.
    
    Args:
        directory (str): Path to the directory containing YAML files.
        
    Returns:
        list: A list of dictionaries, each containing the data from a YAML file.
        Each dictionary is augmented with a 'filename' key containing the original
        filename.
        
    Raises:
        SystemExit: If the directory does not exist.
    """
    all_data = []
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        exit(1)

    for filename in sorted(os.listdir(directory)):
        if filename.endswith(".yaml") or filename.endswith(".yml"):
            filepath = os.path.join(directory, filename)
            print("Reading file:", filepath)
            try:
                with open(filepath, "r", encoding="utf-8") as file:
                    data = yaml.safe_load(file) or {}  # Handle empty files
                    data["filename"] = filename
                    all_data.append(data)
            except yaml.YAMLError as e:
                print(f"Error parsing {filename}: {e}")
            except Exception as e:
                print(f"Unexpected error with {filename}: {e}")

    return all_data