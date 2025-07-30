#!/usr/bin/env python3
"""
Script to fix swagger client imports by converting absolute imports to relative imports.
This script processes Python files within each 'swagger_client' directory
(e.g., src/streetmanager/work/swagger_client, src/streetmanager/geojson/swagger_client, etc.).

For each Python file, it:
1. Calculates the necessary relative import prefix ('.', '..', etc.) based on the
   file's depth relative to its 'swagger_client' root directory.
2. Provides specific, robust fixes for 'swagger_client/__init__.py' and
   'swagger_client/api/__init__.py' to ensure correct package structure.
3. For all other files, converts absolute imports like 'from swagger_client.module import Name'
   to 'from <prefix>.module import Name'.
"""

import re
from pathlib import Path

def convert_imports_in_file(file_path: Path, swagger_client_root: Path, project_root: Path):
    """
    Converts absolute 'swagger_client.' imports to relative imports in a single file.
    Prioritizes specific fixes for __init__.py files.
    """
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return
    
    original_content = content
    current_filename = file_path.name
    current_file_parent_dir_name = file_path.parent.name
    is_in_swagger_client_root = (file_path.parent == swagger_client_root)
    is_in_api_subfolder = (current_file_parent_dir_name == "api" and file_path.parent.parent == swagger_client_root)

    # --- Specific fix for the main __init__.py of a swagger_client package ---
    # (e.g., src/streetmanager/work/swagger_client/__init__.py)
    if current_filename == "__init__.py" and is_in_swagger_client_root:
        # This __init__.py should expose DefaultApi from its 'api' subpackage.
        # Change "from .default_api import DefaultApi" (common from codegen) or
        # "from swagger_client.default_api import DefaultApi" or similar variations
        # to "from .api import DefaultApi".
        # This regex looks for the "# import apis into sdk package" comment block.
        content = re.sub(
            r'(# import apis into sdk package\\s*\\n\\s*from\\s+)(?:swagger_client\.|\.)(?:api\.)?default_api(\\s+import\\s+DefaultApi)',
            r'\\1.api\\2', # Ensures it becomes "from .api import DefaultApi"
            content,
            flags=re.IGNORECASE # To catch DefaultApi or defaultApi if casing varies
        )
        # Ensure other direct imports (api_client, configuration, models) are single-dot relative
        # if they were originally 'from swagger_client.X'
        content = re.sub(r'from swagger_client\\.api_client', 'from .api_client', content)
        content = re.sub(r'from swagger_client\\.configuration', 'from .configuration', content)
        content = re.sub(r'import swagger_client\\.api_client', 'import .api_client', content)
        content = re.sub(r'import swagger_client\\.configuration', 'import .configuration', content)
        content = re.sub(r'from swagger_client\\.models', 'from .models', content)
        content = re.sub(r'import swagger_client\\.models', 'import .models', content)

    # --- Specific fix for swagger_client/api/__init__.py ---
    elif current_filename == "__init__.py" and is_in_api_subfolder:
        # This file must import DefaultApi from its sibling default_api.py.
        # Change "from swagger_client.api.default_api import DefaultApi" (original codegen)
        # or "from ..api.default_api import DefaultApi" (potential previous incorrect fix)
        # or any other variation to "from .default_api import DefaultApi".
        # This regex looks for the "# import apis into api package" comment block.
        content = re.sub(
            r'(# import apis into api package\\s*\\n\\s*from\\s+)(?:swagger_client\.api\.|\.\.api\.|\.\.\.\.api\.|\.)default_api(\\s+import\\s+DefaultApi)',
            r'\\1.default_api\\2', # Ensures it becomes "from .default_api import DefaultApi"
            content,
            flags=re.IGNORECASE
        )
    
    # --- General rules for all other files ---
    else:
        try:
            relative_dir_of_file = file_path.parent.relative_to(swagger_client_root)
        except ValueError:
            print(f"Error: File {file_path} does not seem to be under swagger_client_root {swagger_client_root}")
            return
        depth = len(relative_dir_of_file.parts)
        dot_prefix = "." + "." * depth

        # Convert 'from swagger_client.sub.module' to 'from <dot_prefix>.sub.module'
        content = re.sub(r'from swagger_client\\.([\\w.]+)', rf'from {dot_prefix}.\\1', content)
        # Convert 'import swagger_client.sub.module' to 'import <dot_prefix>.sub.module'
        content = re.sub(r'import swagger_client\\.([\\w.]+)', rf'import {dot_prefix}.\\1', content)

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
            
            python_files.sort()

            for file_path in python_files:
                convert_imports_in_file(file_path, swagger_client_root, project_root)
        else:
            print(f"Directory not found, skipping: {swagger_client_root.relative_to(project_root)}")

    print("\nImport fixing process completed.")

if __name__ == '__main__':
    main() 