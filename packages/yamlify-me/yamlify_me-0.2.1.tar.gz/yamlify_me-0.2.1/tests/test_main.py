import unittest
import sys
import os
import tempfile
import shutil
import io
from contextlib import redirect_stdout

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from yamlify import main
from yamlify.main import parse_arguments, get_version


class TestMain(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for output files
        self.temp_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        # Clean up temporary directory and restore original directory
        os.chdir(self.original_dir)
        shutil.rmtree(self.temp_dir)

    def test_main_as_library(self):
        """Test using main as a library function."""
        # Call main with explicit parameters and write_files=False
        result = main(
            input_dir=os.path.abspath(os.path.join(os.path.dirname(__file__), 'data/cars')),
            template_path=os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates/template_single.j2')),
            output='output.txt',
            write_files=False,
            verbose=False
        )

        # Check the result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['filename'], 'output.txt')
        self.assertIn('Toyota Corolla 2020 00001.yaml', result[0]['content'])
        self.assertIn('Honda Civic 2019 00002.yaml', result[0]['content'])
        self.assertIn('Audi A3 2017 00003.yaml', result[0]['content'])

        # Verify that no files were written
        self.assertEqual(len(os.listdir(self.temp_dir)), 0)

    def test_main_with_file_writing(self):
        """Test using main with file writing enabled."""
        # Call main with explicit parameters and write_files=True
        result = main(
            input_dir=os.path.abspath(os.path.join(os.path.dirname(__file__), 'data/cars')),
            template_path=os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates/template_single.j2')),
            output='output.txt',
            write_files=True,
            verbose=False
        )

        # Check the result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['filename'], 'output.txt')

        # Verify that the file was written
        self.assertTrue(os.path.exists('output.txt'))

        # Check the file content
        with open('output.txt', 'r') as f:
            content = f.read()
            self.assertIn('Toyota Corolla 2020 00001.yaml', content)
            self.assertIn('Honda Civic 2019 00002.yaml', content)
            self.assertIn('Audi A3 2017 00003.yaml', content)

    def test_main_with_multiple_files(self):
        """Test using main to generate multiple output files."""
        # Call main with output_filename_template
        result = main(
            input_dir=os.path.abspath(os.path.join(os.path.dirname(__file__), 'data/cars')),
            template_path=os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates/template_multi.j2')),
            output_filename_template='{make}.txt',
            write_files=True,
            verbose=False
        )

        # Check the result
        self.assertEqual(len(result), 3)

        # Verify that the files were written
        self.assertTrue(os.path.exists('Toyota.txt'))
        self.assertTrue(os.path.exists('Honda.txt'))
        self.assertTrue(os.path.exists('Audi.txt'))

        # Check the file contents
        with open('Toyota.txt', 'r') as f:
            content = f.read()
            self.assertIn('Toyota Corolla 2020 00001.yaml', content)

        with open('Honda.txt', 'r') as f:
            content = f.read()
            self.assertIn('Honda Civic 2019 00002.yaml', content)

        with open('Audi.txt', 'r') as f:
            content = f.read()
            self.assertIn('Audi A3 2017 00003.yaml', content)

    def test_version_flag(self):
        """Test that the --version flag works correctly."""
        # Capture stdout and handle SystemExit
        output = io.StringIO()
        with self.assertRaises(SystemExit) as cm, redirect_stdout(output):
            parse_arguments(['--version'])

        # Check that the exit code is 0 (success)
        self.assertEqual(cm.exception.code, 0)

        # Check that the output contains version information
        version_output = output.getvalue().strip()

        # Get the version
        version = get_version()

        # Check that the output contains the version
        self.assertIn(version, version_output)

        # Check that the version is in the expected format (x.y.z)
        self.assertRegex(version, r'\d+\.\d+(\.\d+)?')


if __name__ == '__main__':
    unittest.main()
