"""
Utilities Module - Software Detailed Design

1. Module Purpose and Scope:
   This module provides utility functions for the yamlify application,
   such as displaying the structure of data objects.

2. Component Architecture:
   - Single-responsibility module focused on utility operations
   - Functional approach with pure functions

3. Data Flow:
   a. Input:
      - Data objects to analyze or manipulate
   b. Processing:
      - Analyze data structure
      - Format output
   c. Output:
      - Printed information or transformed data

4. Interfaces:
   - Public Functions:
     * show_structure: Displays the structure of a dictionary

5. Dependencies:
   - Standard Python libraries only

6. Error Handling Strategy:
   - Type checking for input parameters
   - Graceful handling of edge cases

7. Performance Considerations:
   - Efficient data structure traversal
   - Minimal memory footprint

8. Security Considerations:
   - No security concerns for utility functions

9. Testing Strategy:
   - Unit tests for all functionality
   - Test cases for valid inputs, edge cases, and error conditions

10. Maintenance Considerations:
    - Comprehensive docstrings following standard format
    - Clear code structure with logical separation of concerns
"""


def show_structure(data, indent=0):
    """
    Recursively prints the structure of a dictionary.
    
    This function traverses a dictionary and prints its structure, showing
    the keys, value types, and nested structures. It's useful for analyzing
    complex data structures.
    
    Args:
        data (dict): The dictionary to show the structure of.
        indent (int, optional): The current indentation level (used for nested structures).
            Defaults to 0.
    """
    for key, value in data.items():
        print(" " * indent + f"{key}: {type(value).__name__}")
        if isinstance(value, dict):
            show_structure(value, indent + 2)
        elif isinstance(value, list) and value and isinstance(value[0], dict):
            print(" " * (indent + 2) + "[" + str(len(value)) + "]")
            show_structure(value[0], indent + 4)