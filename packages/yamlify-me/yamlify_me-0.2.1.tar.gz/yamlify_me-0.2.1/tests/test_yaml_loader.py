import unittest
import sys
import os
import tempfile
import shutil
import yaml

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from yamlify.yaml_loader import load_yaml_files, load_yaml_files_recursively


class TestYamlLoader(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a directory structure for testing recursive loading
        self.cars_dir = os.path.join(self.temp_dir, "cars")
        self.persons_dir = os.path.join(self.temp_dir, "persons")
        os.makedirs(self.cars_dir)
        os.makedirs(self.persons_dir)
        
        # Create test YAML files
        self.create_test_yaml_files()

    def tearDown(self):
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir)

    def create_test_yaml_files(self):
        # Create car YAML files
        car1_data = {"make": "Toyota", "model": "Corolla", "year": 2020}
        car2_data = {"make": "Honda", "model": "Civic", "year": 2019}
        
        with open(os.path.join(self.cars_dir, "car1.yaml"), "w") as f:
            yaml.dump(car1_data, f)
        with open(os.path.join(self.cars_dir, "car2.yaml"), "w") as f:
            yaml.dump(car2_data, f)
            
        # Create person YAML files
        person1_data = {"name": "John Doe", "email": "john@example.com"}
        person2_data = {"name": "Jane Smith", "email": "jane@example.com"}
        
        with open(os.path.join(self.persons_dir, "person1.yaml"), "w") as f:
            yaml.dump(person1_data, f)
        with open(os.path.join(self.persons_dir, "person2.yaml"), "w") as f:
            yaml.dump(person2_data, f)

    def test_load_yaml_files(self):
        """Test loading YAML files from a directory (non-recursive)."""
        # Load YAML files from the cars directory
        data = load_yaml_files(self.cars_dir)
        
        # Check that the correct number of files were loaded
        self.assertEqual(len(data), 2)
        
        # Check that the data contains the expected content
        makes = [item.get('make') for item in data]
        self.assertIn('Toyota', makes)
        self.assertIn('Honda', makes)
        
        # Check that each item has a filename key
        for item in data:
            self.assertIn('filename', item)

    def test_load_yaml_files_nonexistent_directory(self):
        """Test loading YAML files from a non-existent directory."""
        # This should exit the program, so we need to capture the exit
        with self.assertRaises(SystemExit):
            load_yaml_files("/nonexistent/directory")

    def test_load_yaml_files_recursively(self):
        """Test loading YAML files recursively from a directory."""
        # Load YAML files recursively from the temp directory
        data = load_yaml_files_recursively(self.temp_dir)
        
        # Check the structure of the returned data
        self.assertIn('elements', data)
        self.assertIn('children', data)
        self.assertIn('directory', data)
        self.assertIn('dirname', data)
        
        # Check that the children dictionary contains the expected subdirectories
        self.assertIn('cars', data['children'])
        self.assertIn('persons', data['children'])
        
        # Check that each subdirectory contains the expected number of files
        self.assertEqual(len(data['children']['cars']['elements']), 2)
        self.assertEqual(len(data['children']['persons']['elements']), 2)
        
        # Check that the data contains the expected content
        car_makes = [item.get('make') for item in data['children']['cars']['elements']]
        self.assertIn('Toyota', car_makes)
        self.assertIn('Honda', car_makes)
        
        person_names = [item.get('name') for item in data['children']['persons']['elements']]
        self.assertIn('John Doe', person_names)
        self.assertIn('Jane Smith', person_names)

    def test_load_yaml_files_recursively_nonexistent_directory(self):
        """Test loading YAML files recursively from a non-existent directory."""
        # This should exit the program, so we need to capture the exit
        with self.assertRaises(SystemExit):
            load_yaml_files_recursively("/nonexistent/directory")


if __name__ == '__main__':
    unittest.main()