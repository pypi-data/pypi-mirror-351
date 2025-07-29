# Yamlify Me

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/yamlify-me.svg)](https://badge.fury.io/py/yamlify-me)

Yamlify Me is a powerful document generation tool and Python library that combines YAML data with Jinja2 templates to create customized documents. It provides a flexible and efficient way to generate documentation, reports, configuration files, and other text-based outputs from structured data.

## Features

- **Data Aggregation**: Read and merge data from multiple YAML files in a folder
- **Recursive Loading**: Process data hierarchically from nested directory structures
- **Custom Processing**: Manipulate data with custom processors before rendering
- **Flexible Templating**: Render data with Jinja2 templates with support for filters and control structures
- **Multiple Output Formats**: Generate single or multiple output files from the same data
- **Command-line Interface**: Easy-to-use CLI for quick document generation
- **Programmatic API**: Clean Python API for integration into other applications

## Installation

### From PyPI

```bash
pip install yamlify-me
```

### From Source

```bash
git clone https://github.com/JensKlimke/yamlify.git
cd yamlify
pip install -e .
```

## Command-line Usage

### Basic Syntax

```bash
yamlify <input_dir> <template_path> [options]
```

### Arguments

- `input_dir`: Path to the directory containing YAML files
- `template_path`: Path to the Jinja2 template file

### Options

- `-r, --recursive`: Load files recursively from folders and subfolders
- `-p, --processor`: Python module with a process function to manipulate data before rendering
- `--processor-path`: Path to the processor module if not in the working directory
- `-o, --output`: Path to save the rendered document file (default: output.html)
- `-f, --output_filename_template`: Template for generating multiple output files
- `-l, --list_structure`: List the data structure for analysis
- `--version`: Show the version and exit

For detailed help:

```bash
yamlify --help
```

## Usage Examples

### Scenario 1: Creating multiple doc files from multiple data files

Define data in the files ```data/cars/00001.yaml``` and ```data/cars/00002.yaml```:

``` yaml
make: Toyota
model: Corolla
year: 2020
```

``` yaml
make: Honda
model: Civic
year: 2019
```

Define a template file ```templates/template_multi.j2```:

```
{{ make }} {{ model }} {{ year }} {{ filename }}
```

The command ```yamlify data/cars/ templates/template_multi.j2 -f {make}.txt```generates the file ```Toyota.txt``` and ```Honda.txt```:

``` txt
Toyota Corolla 2020 00001.yaml
```

``` txt
Honda Civic 2019 00002.yaml
```

_To test this scenario, please check the tests folder._

### Scenario 2: Creating a single doc file from multiple data files

Define data in the files ```data/cars/00001.yaml``` and ```data/cars/00002.yaml``` as above.

Define a template file ```templates/template_single.j2```:

```
{% for car in data %}{{ car.make }} {{ car.model }} {{ car.year }} {{ car.filename }}
{% endfor %}
```

The command ```yamlify data/cars/ templates/template_single.j2 -o output.txt``` generates the file ```output.txt```:

``` txt
Toyota Corolla 2020 00001.yaml
Honda Civic 2019 00002.yaml

```

_To test this scenario, please check the tests folder._

### Scenario 3: Creating a single doc file from multiple data files with recursive subfolders

Define data in the files ```data/cars/00001.yaml``` and ```data/cars/00002.yaml``` as above and add data file ```data/persons/john.yaml``` and ```data/persons/jane.yaml```:

``` yaml
name: John Doe
```

``` yaml
name: Jane Smith
```

Define a template file ```templates/template_recursive.j2```:

```
{% for car in data.children.cars.elements %}{{ car.model }}
{% endfor %}
{% for person in data.children.persons.elements %}{{ person.name }}
{% endfor %}
```

The command ```yamlify data/ templates/template_single.j2 -o output.txt -r``` generates the file ```output.txt```:

``` txt
Corolla
Civic

Jane Smith
John Doe

```

**Explanation:** The data is merged from multiple files and added to a data structure with the following structure (and a few more fields):

``` python
{
    'children': {
        'cars': {
            'elements': [
                {'filename': '00001.yaml', 'make': 'Toyota', 'model': 'Corolla', 'year': 2020},
                {'filename': '00002.yaml', 'make': 'Honda', 'model': 'Civic', 'year': 2019}
            ]
        },
        'persons': {
            'elements': [
                {'filename': 'john.yaml', 'name': 'John Doe'},
                {'filename': 'jane.yaml', 'name': 'Jane Smith'}
            ]
        }
    }
}
```

### Scenario 4: Review the data structure

To see the complete data structure, create a template file ```templates/template_structure.j2```:

```
{{ data | json }}
```

Execute the command ```yamlify data/ templates/template_structure.j2 -o output.txt -r ```. This will generate the file ```output.txt``` with the complete data structure in JSON format.

### Scenario 5: Manipulate data before rendering (here: link data)

Create the files ```data/cars/00001.yaml``` and ```data/cars/00002.yaml``` and ```data/cars/00003.yaml```:

``` yaml
make: Toyota
model: Corolla
year: 2020
owner: john
```

``` yaml
make: Honda
model: Civic
year: 2019
owner: jane
```

``` yaml
make: Audi
model: A3
year: 2017
owner: john
```

Create the files ```data/persons/john.yaml``` and ```data/persons/jane.yaml```:

``` yaml
name: John Doe
email: john.doe@example.com
age: 30
```

``` yaml
name: Jane Smith
email: jane.smith@example.com
age: 25
```


Create a module file ```modules/link_refs.py```:

``` python

def process(data):
    # Create index of persons
    data['person_index'] = {}
    for person in data['children']['persons']['elements']:
        data['person_index'][person['key']] = person
    for car in data['children']['cars']['elements']:
        if 'owner' in car and data['person_index'][car['owner']]:
            car['owner'] = data['person_index'][car['owner']]
        else:
            car['owner'] = None
    return data
```

This code reads the persons from the merged data structure and creates a person index (dictionary) using the key field, which is generated from the file name.
Then it iterates over the cars and replaces the owner field with the person object from the index. Within the renderer, the owner is now available as a linked object.

Create a template file ```templates/template_linked.j2```:

```
| Vehicle | Owner |
|---|---|
{% for car in data.children.cars.elements %}|{{ car.make }} {{ car.model }}|{{ car.owner.name }}|
{% endfor %}
```

The command ```yamlify data/ templates/template_linked.j2 -o output.md -r --processor-path modules -p link_refs``` generates the file ```output.md```:

``` markdown
| Vehicle | Owner |
|---|---|
|Toyota Corolla|John Doe|
|Honda Civic|Jane Smith|
|Audi A3|John Doe|
```

The rendered version of the table looks like this:

| Vehicle        | Owner      |
|----------------|------------|
| Toyota Corolla | John Doe   |
| Honda Civic    | Jane Smith |
| Audi A3        | John Doe   |


_To test this scenario, please check the tests folder._

## Architecture

Yamlify is designed with a modular architecture that separates concerns and promotes maintainability:

- **yaml_loader**: Handles loading YAML files from directories
- **template_renderer**: Manages template rendering with Jinja2
- **utils**: Provides utility functions for data manipulation and analysis
- **convert**: Orchestrates the conversion process
- **data**: Provides legacy data processing functionality
- **main**: Implements the command-line interface

## API Documentation

### Core Functions

#### `convert(input_dir, template_path, output=None, output_filename_template=None, list_structure=False, processor=None, processor_path=None, recursive=False)`

Orchestrates the entire conversion process.

- **Parameters**:
  - `input_dir` (str): Path to the directory containing YAML files
  - `template_path` (str): Path to the Jinja2 template file
  - `output` (str, optional): Path to save the rendered document file
  - `output_filename_template` (str, optional): Template for generating multiple output filenames
  - `list_structure` (bool, optional): Whether to print the structure of the loaded data
  - `processor` (str, optional): Name of a Python module with a process function
  - `processor_path` (str, optional): Path to the processor module
  - `recursive` (bool, optional): Whether to load YAML files recursively from subdirectories

- **Returns**:
  - List of dictionaries, each containing:
    - 'filename': The output filename
    - 'content': The rendered content

#### `load_yaml_files(directory)`

Loads YAML files from a directory (non-recursive).

- **Parameters**:
  - `directory` (str): Path to the directory containing YAML files

- **Returns**:
  - List of dictionaries, each containing the data from a YAML file

#### `load_yaml_files_recursively(directory)`

Recursively loads YAML files from a directory and its subdirectories.

- **Parameters**:
  - `directory` (str): Path to the directory containing YAML files

- **Returns**:
  - Dictionary with a hierarchical structure representing the directory tree and file contents

#### `render_template(template_path, merged_data)`

Renders a Jinja2 template with the provided data.

- **Parameters**:
  - `template_path` (str): Path to the Jinja2 template file
  - `merged_data` (dict): Data to render the template with

- **Returns**:
  - Rendered template as a string

### Custom Template Filters

#### `markdown_to_html(text)`

Converts markdown text to HTML.

- **Usage in templates**:
  ```
  {{ markdown_text | markdown }}
  ```

#### `to_json(data)`

Converts data to a JSON string.

- **Usage in templates**:
  ```
  {{ data | json }}
  ```

## Creating Custom Processors

Custom processors allow you to manipulate the data before rendering. A processor is a Python module with a `process` function that takes the loaded data as input and returns the modified data.

Example processor:

```python
def process(data):
    # Add a timestamp to each element
    import datetime
    timestamp = datetime.datetime.now().isoformat()

    if 'elements' in data:
        for element in data['elements']:
            element['timestamp'] = timestamp

    # Process nested children recursively
    if 'children' in data:
        for child_name, child_data in data['children'].items():
            process(child_data)

    return data
```

## Contributing

Contributions are welcome! Here's how you can contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

Please make sure to update tests as appropriate and follow the code style of the project.

## License

MIT - see [LICENSE](LICENSE) file for details
