from .convert import convert
import argparse
import importlib.metadata
import os
import re


def get_version():
    """
    Get the package version.

    First tries to get the version from the installed package metadata.
    If that fails (e.g., when running from source), tries to read the version
    from pyproject.toml. If that fails, uses the __version__ variable from __init__.py.

    Returns:
        str: The package version.
    """
    try:
        return importlib.metadata.version('yamlify-me')
    except importlib.metadata.PackageNotFoundError:
        # Package is not installed, try to read version from pyproject.toml
        try:
            # Find the pyproject.toml file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            pyproject_path = os.path.join(project_root, 'pyproject.toml')

            if os.path.exists(pyproject_path):
                with open(pyproject_path, 'r') as f:
                    content = f.read()
                    # Use regex to find the version
                    match = re.search(r'version\s*=\s*"([^"]+)"', content)
                    if match:
                        return match.group(1)

            # If we couldn't find the version in pyproject.toml, use the __version__ from __init__.py
            from . import __version__
            return __version__
        except Exception:
            # If all else fails, return a default
            return "unknown"


def parse_arguments(args=None):
    """
    Parse command-line arguments.

    Args:
        args (list, optional): List of arguments to parse. If None, uses sys.argv.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Generate a document (html, markdown, text, ...) from YAML files using a Jinja2 templates."
    )
    parser.add_argument(
        "input_dir",
        help="Path to the directory containing YAML files. If the directory is nested, use recursive arg (-r, --recursive).",
    )
    parser.add_argument("template_path", help="Path to the Jinja2 template file.")
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        default=False,
        help="Loads the files recursively from the folder and subfolders.",
    )
    parser.add_argument(
        "-p",
        "--processor",
        required=False,
        help="A python module with process function to manipulate the loaded data before rendering.",
    )
    parser.add_argument(
        "--processor-path",
        required=False,
        help="The path of the processor module if not in the working dir.",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=False,
        default="output.html",
        help="Path to save the rendered document file.",
    )
    parser.add_argument(
        "-f",
        "--output_filename_template",
        required=False,
        default=None,
        help="Define a file template to generate multiple output files, one for each input file.",
    )
    parser.add_argument(
        "-l",
        "--list_structure",
        action="store_true",
        default=False,
        help="Lists the data structure (for analysis).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {get_version()}",
        help="Show the version and exit.",
    )
    return parser.parse_args(args)


def main(input_dir=None, template_path=None, output="output.html", 
         output_filename_template=None, list_structure=False, 
         processor=None, processor_path=None, recursive=False, 
         write_files=True, verbose=True, return_result=None):
    """
    Main function for the yamlify package. Can be used both as a command-line tool
    and as a library function.

    Args:
        input_dir (str, optional): Path to the directory containing YAML files.
            If None, uses the value from command-line arguments.
        template_path (str, optional): Path to the Jinja2 template file.
            If None, uses the value from command-line arguments.
        output (str, optional): Path to save the rendered document file.
            Defaults to "output.html".
        output_filename_template (str, optional): Template for generating multiple
            output filenames. Defaults to None.
        list_structure (bool, optional): Whether to print the structure of the
            loaded data. Defaults to False.
        processor (str, optional): Name of a Python module with a process function.
            Defaults to None.
        processor_path (str, optional): Path to the processor module.
            Defaults to None.
        recursive (bool, optional): Whether to load YAML files recursively.
            Defaults to False.
        write_files (bool, optional): Whether to write output files to disk.
            Defaults to True.
        verbose (bool, optional): Whether to print status messages.
            Defaults to True.
        return_result (bool, optional): Whether to return the result.
            If None, returns the result only when not called from command line.
            Defaults to None.

    Returns:
        list or None: If return_result is True, returns a list of dictionaries, each containing:
            - 'filename': The output filename
            - 'content': The rendered content
            If return_result is False, returns None.
    """
    # Flag to indicate whether the function was called with both input_dir and template_path provided
    called_as_library = input_dir is not None and template_path is not None

    if verbose:
        print("Running yamlify")

    # If input_dir or template_path are not provided, get them from command-line arguments
    if input_dir is None or template_path is None:
        args = parse_arguments()

        # Use command-line arguments for any parameters that weren't provided
        input_dir = input_dir or args.input_dir
        template_path = template_path or args.template_path
        output = output if output != "output.html" else args.output
        output_filename_template = output_filename_template or args.output_filename_template
        list_structure = list_structure or args.list_structure
        processor = processor or args.processor
        processor_path = processor_path or args.processor_path
        recursive = recursive or args.recursive

    # Read data and convert
    result = convert(
        input_dir=input_dir,
        template_path=template_path,
        output=output,
        output_filename_template=output_filename_template,
        list_structure=list_structure,
        processor=processor,
        processor_path=processor_path,
        recursive=recursive,
    )

    # Generate output files if requested
    if write_files:
        for item in result:
            # Get filename and content
            filename = item["filename"]
            content = item["content"]
            # Write files
            with open(filename, "w", encoding="utf-8") as file:
                file.write(content)
            # Log if verbose
            if verbose:
                print(f"Output file '{filename}' has been generated successfully.")

    # Determine whether to return the result
    if return_result is None:
        # If called as a library function, return the result
        # If called from command line, don't return the result
        return result if called_as_library else None
    elif return_result:
        return result
    else:
        return None


if __name__ == "__main__":
    main(return_result=False)
