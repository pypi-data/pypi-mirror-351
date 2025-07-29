# h7-file-finder

Core utility classes for file and path finding in Python projects.

## Installation

```bash
pip install h7-file-finder
```

## Features

- Find project root directory based on marker files
- Locate specific files within a project
- Find environment files and project-specific folders
- Support for custom markers and search paths

## Usage

```python
from h7_file_finder import find_project_root, find_file_in_project

# Find project root
project_root = find_project_root()
print(f"Project root found at: {project_root}")

# Find a specific file
env_file = find_file_in_project(".env")
print(f"Found .env file at: {env_file}")

# Find with custom markers
custom_markers = [".git", "requirements.txt"]
project_root_custom = find_project_root(markers=custom_markers)
```

## Requirements

- Python 3.7+
- python-dotenv

## License

MIT License - Copyright (c) 2025 Roger Mori
