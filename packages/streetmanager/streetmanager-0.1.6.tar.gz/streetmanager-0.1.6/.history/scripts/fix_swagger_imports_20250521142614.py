#!/usr/bin/env python3
"""
Script to fix swagger client imports by converting absolute imports to relative imports.
This script processes Python files within each 'swagger_client' directory
(e.g., src/streetmanager/work/swagger_client, src/streetmanager/geojson/swagger_client, etc.).

For each Python file, it:
1. Calculates the necessary relative import prefix ('.', '..', etc.) based on the
   file's depth relative to its 'swagger_client' root directory.
2. Converts absolute imports like 'from swagger_client.module import Name' to
   'from <prefix>.module import Name'.
3. Converts absolute imports like 'import swagger_client.module' to
   'import <prefix>.module'.
4. Ensures the main __init__.py of each swagger_client package correctly
   exports 'DefaultApi' (and other core components) by importing them from
   its submodules (e.g., 'from .api import DefaultApi').
"""

import re
from pathlib import Path

def convert_imports_in_file(file_path: Path, swagger_client_root: Path, project_root: Path):
    """
    Converts absolute 'swagger_client.' imports to relative imports in a single file.
    Also, handles specific import patterns for __init__.py files.
    """
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return
    
    original_content = content

    # Determine the relative path from the swagger_client_root to the current file's directory.
    # This determines the number of dots needed for the relative import prefix.
    try:
        relative_dir_of_file = file_path.parent.relative_to(swagger_client_root)
    except ValueError:
        # This can happen if file_path is not under swagger_client_root, which shouldn't occur with current logic.
        print(f"Error: File {file_path} does not seem to be under swagger_client_root {swagger_client_root}")
        return

    # Depth is the number of directory levels from swagger_client_root to the file's directory.
    # e.g., 0 for files directly in swagger_client_root (e.g., swagger_client/api_client.py)
    #       1 for files in swagger_client_root/api/ (e.g., swagger_client/api/default_api.py)
    depth = len(relative_dir_of_file.parts)

    # Calculate the dot_prefix:
    # - If depth is 0 (file is in swagger_client_root), prefix is "."
    # - If depth is 1 (file is in swagger_client_root/api), prefix is ".."
    # - And so on.
    dot_prefix = "." + "." * depth

    # General rule: Convert 'from swagger_client.sub.module' to 'from <dot_prefix>.sub.module'
    content = re.sub(r'from swagger_client\.([\w.]+)', rf'from {dot_prefix}.\1', content)

    # General rule: Convert 'import swagger_client.sub.module' to 'import <dot_prefix>.sub.module'
    content = re.sub(r'import swagger_client\.([\w.]+)', rf'import {dot_prefix}.\1', content)

    # Specific fix for the main __init__.py of a swagger_client package
    # (e.g., src/streetmanager/work/swagger_client/__init__.py)
    if file_path.name == "__init__.py" and file_path.parent == swagger_client_root:
        # This __init__.py should expose APIs, e.g., DefaultApi.
        # It often imports DefaultApi from its 'api' subpackage.
        # We want to ensure 'from .api import DefaultApi' or 'from .api.default_api import DefaultApi'.
        # The `api/__init__.py` should itself export DefaultApi via `from .default_api import DefaultApi`.
        # So, `from .api import DefaultApi` is preferred in this top-level `__init__.py`.

        # Correct a common misconfiguration where it might try to import directly from a sibling default_api.py
        # (e.g., "from .default_api import DefaultApi") instead of from the "api" subpackage.
        # This pattern looks for "# import apis into sdk package" followed by the problematic import.
        content = re.sub(
            r'(# import apis into sdk package\s*\n\s*)from \.default_api import DefaultApi',
            r'\1from .api import DefaultApi',
            content
        )
        # If the generator produced `from .api.default_api import DefaultApi` (after general replacements),
        # that is also acceptable and the above regex won't modify it.

    # Specific fix for swagger_client/api/__init__.py
    # This file should import its own contents using single-dot relative imports.
    # e.g., 'from .default_api import DefaultApi'
    if file_path.name == "__init__.py" and file_path.parent.name == "api" and file_path.parent.parent == swagger_client_root:
        # If the general rule (due to original `from swagger_client.api.default_api`) changed an import to
        # something like 'from ..api.default_api import DefaultApi', it's wrong for this file.
        # It should be 'from .default_api import DefaultApi'.
        content = re.sub(
            r'from \.\.api\.default_api import DefaultApi', # Problematic pattern after general rule
            r'from .default_api import DefaultApi',         # Corrected pattern
            content
        )

    if content != original_content:
        print(f"Updating imports in: {file_path.relative_to(project_root)}")
        try:
            file_path.write_text(content, encoding='utf-8')
        except Exception as e:
            print(f"Error writing file {file_path}: {e}")
    else:
        print(f"No import changes needed for: {file_path.relative_to(project_root)}")

def main():
    # Determine the project root (assuming script is in 'scripts/' subdirectory of project root)
    try:
        project_root = Path(__file__).resolve().parent.parent
    except NameError: # Fallback if __file__ is not defined (e.g. interactive)
        project_root = Path(".").resolve()

    print(f"Project root identified as: {project_root}")
    base_src_dir = project_root / 'src' / 'streetmanager'

    submodule_types = ["work", "geojson", "lookup"]

    for submodule_name in submodule_types:
        swagger_client_root = base_src_dir / submodule_name / "swagger_client"
        if swagger_client_root.is_dir():
            print(f"\nProcessing swagger client module: {swagger_client_root.relative_to(project_root)}")
            
            python_files = list(swagger_client_root.rglob('*.py'))
            if not python_files:
                print(f"No Python files found in {swagger_client_root.relative_to(project_root)}")
                continue
            
            # Sort files for consistent processing order (optional, but good for logs)
            python_files.sort()

            for file_path in python_files:
                # print(f"--- Analyzing: {file_path.relative_to(project_root)}") # Verbose
                convert_imports_in_file(file_path, swagger_client_root, project_root)
        else:
            print(f"Directory not found, skipping: {swagger_client_root.relative_to(project_root)}")

    print("\nImport fixing process completed.")

if __name__ == '__main__':
    main() 