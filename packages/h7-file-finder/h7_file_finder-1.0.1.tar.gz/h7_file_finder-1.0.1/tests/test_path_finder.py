import unittest
from pathlib import Path
import os
import sys

# Add the src directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from h7_file_finder import find_project_root, find_file_in_project

class TestPathFinder(unittest.TestCase):
    
    def test_find_project_root(self):
        """Test that find_project_root returns a Path object"""
        # Create a temporary marker file
        temp_marker = Path(__file__).parent / ".test_marker"
        try:
            with open(temp_marker, 'w') as f:
                f.write("test marker")
            
            # Test with custom marker
            root = find_project_root(start_path=Path(__file__).parent, markers=[".test_marker"])
            self.assertIsInstance(root, Path)
            self.assertEqual(root, Path(__file__).parent)
            
        finally:
            # Clean up
            if temp_marker.exists():
                temp_marker.unlink()
    
    def test_find_file_in_project(self):
        """Test that find_file_in_project can find this test file"""
        this_file = Path(__file__).name
        found_file = find_file_in_project(this_file, start_path=Path(__file__).parent)
        self.assertEqual(found_file, Path(__file__))
    
    def test_file_not_found(self):
        """Test that find_file_in_project raises FileNotFoundError for non-existent files"""
        with self.assertRaises(FileNotFoundError):
            find_file_in_project("non_existent_file.xyz", 
                                start_path=Path(__file__).parent,
                                search_parents=False)

if __name__ == '__main__':
    unittest.main()
