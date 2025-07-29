"""
Documentation for the h7_file_finder package.

This package provides utilities for finding files and directories in a project.
"""

# Package version
__version__ = "1.0.0"

# Import main functions to make them available at package level
from .path_finder import (
    find_project_root as find_project_root,
    find_file_in_project as find_file_in_project,
    find_env_file as find_env_file,
    find_root_folder as find_root_folder
)
