from pathlib import Path
from typing import List, Optional, Union


def find_project_root(start_path: Optional[Union[str, Path]] = None,
                      markers: Optional[List[str]] = None) -> Path:
    default_markers = [".env", ".git", "pyproject.toml", "setup.py", "requirements.txt"]
    markers = markers or default_markers

    if start_path is None:
        start_path = Path.cwd()
    else:
        start_path = Path(start_path).resolve()

    current_path = start_path
    while current_path.parent != current_path:  # Stop at root
        if any((current_path / marker).exists() for marker in markers):
            return current_path
        current_path = current_path.parent

    raise FileNotFoundError(
        f"Project root not found. Searched for markers: {markers} "
        f"starting from {start_path}"
    )

def find_file_in_project(filename: str,
                         start_path: Optional[Union[str, Path]] = None,
                         search_parents: bool = True) -> Path:
    if start_path is None:
        start_path = Path.cwd()
    else:
        start_path = Path(start_path).resolve()

    current_path = start_path

    # First check in the start directory
    target_file = current_path / filename
    if target_file.exists():
        return target_file

    if search_parents:
        while current_path.parent != current_path:
            target_file = current_path / filename
            if target_file.exists():
                return target_file
            current_path = current_path.parent

    raise FileNotFoundError(
        f"File '{filename}' not found starting from {start_path}"
        f"{' (including parent directories)' if search_parents else ''}"
    )

def find_env_file() -> Path:
    return find_file_in_project(".env")

def find_root_folder(folder_name: str) -> Path:
    if not str:
        raise ValueError("folder_name cannot be None or empty")
    return find_project_root() / folder_name
