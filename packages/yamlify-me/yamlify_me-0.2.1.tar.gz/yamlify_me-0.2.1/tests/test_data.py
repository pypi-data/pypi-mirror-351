import unittest
import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from yamlify.data import read_folder


class TestReadFolder(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()

        # Create an empty directory for testing
        self.empty_dir = os.path.join(self.temp_dir, "empty")
        os.makedirs(self.empty_dir)

        # Create a directory with invalid YAML files
        self.invalid_dir = os.path.join(self.temp_dir, "invalid")
        os.makedirs(self.invalid_dir)
        with open(os.path.join(self.invalid_dir, "invalid.yaml"), "w") as f:
            f.write("invalid: yaml: content:")  # Invalid YAML syntax

    def tearDown(self):
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir)

    def test_read_folder_cars(self):
        """Test reading YAML files from the cars directory."""
        data = []
        index = {}

        # Get the absolute path to the test data directory
        test_dir = os.path.abspath(os.path.dirname(__file__))

        # Call the function with the cars directory
        errors = read_folder(test_dir, "data/cars", data, index)

        # Check that no errors occurred
        self.assertIsNone(errors)

        # Check that the correct number of files were read
        self.assertEqual(len(data), 3)

        # Check that the index contains the expected keys
        car_paths = [
            str(Path(os.path.join(test_dir, "data/cars/00001")).absolute()),
            str(Path(os.path.join(test_dir, "data/cars/00002")).absolute()),
            str(Path(os.path.join(test_dir, "data/cars/00003")).absolute())
        ]
        for path in car_paths:
            self.assertIn(path, index)

        # Check that the data contains the expected content
        makes = [item.get('make') for item in data]
        self.assertIn('Toyota', makes)
        self.assertIn('Honda', makes)
        self.assertIn('Audi', makes)

    def test_read_folder_persons(self):
        """Test reading YAML files from the persons directory."""
        data = []
        index = {}

        # Get the absolute path to the test data directory
        test_dir = os.path.abspath(os.path.dirname(__file__))

        # Call the function with the persons directory
        errors = read_folder(test_dir, "data/persons", data, index)

        # Check that no errors occurred
        self.assertIsNone(errors)

        # Check that the correct number of files were read
        self.assertEqual(len(data), 2)

        # Check that the index contains the expected keys
        person_paths = [
            str(Path(os.path.join(test_dir, "data/persons/john")).absolute()),
            str(Path(os.path.join(test_dir, "data/persons/jane")).absolute())
        ]
        for path in person_paths:
            self.assertIn(path, index)

        # Check that the data contains the expected content
        names = [item.get('name') for item in data]
        self.assertIn('John Doe', names)
        self.assertIn('Jane Smith', names)

    def test_read_folder_nonexistent_directory(self):
        """Test reading from a non-existent directory."""
        data = []
        index = {}

        # Call the function with a non-existent directory
        with self.assertRaises(FileNotFoundError):
            read_folder("/nonexistent", "path", data, index)

    def test_read_folder_empty_directory(self):
        """Test reading from an empty directory."""
        data = []
        index = {}

        # Call the function with an empty directory
        errors = read_folder(self.temp_dir, "empty", data, index)

        # Check that no errors occurred but no files were read
        self.assertIsNone(errors)
        self.assertEqual(len(data), 0)

    def test_read_folder_invalid_yaml(self):
        """Test reading invalid YAML files."""
        data = []
        index = {}

        # Call the function with a directory containing invalid YAML
        errors = read_folder(self.temp_dir, "invalid", data, index)

        # Check that errors were returned
        self.assertIsNotNone(errors)
        self.assertEqual(len(errors), 1)
        self.assertIn("YAML parsing error", errors[0])

    def test_read_folder_invalid_parameters(self):
        """Test with invalid parameters."""
        # Test with invalid directory parameter
        with self.assertRaises(ValueError):
            read_folder(None, "path", [], {})

        # Test with invalid path parameter
        with self.assertRaises(ValueError):
            read_folder("/tmp", None, [], {})

        # Test with invalid data parameter
        with self.assertRaises(ValueError):
            read_folder("/tmp", "path", None, {})

        # Test with invalid index parameter
        with self.assertRaises(ValueError):
            read_folder("/tmp", "path", [], None)


if __name__ == '__main__':
    unittest.main()
