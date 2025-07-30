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

def print_debug_info(file_path: Path, content: str, stage: str):
    print(f"--- DEBUG: {stage} for {file_path.name} ---")
    if file_path.name == "__init__.py" or "default_api.py" in file_path.name:
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if "DefaultApi" in line or "api_client" in line or "configuration" in line or "models" in line or "swagger_client" in line:
                print(f"  L{i+1}: {line}")
    print(f"--- END DEBUG: {stage} for {file_path.name} ---")

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
    print_debug_info(file_path, original_content, "Before processing")

    current_filename = file_path.name
    current_file_parent_dir_name = file_path.parent.name
    is_in_swagger_client_root = (file_path.parent == swagger_client_root)
    is_in_api_subfolder = (current_file_parent_dir_name == "api" and file_path.parent.parent == swagger_client_root)

    if current_filename == "__init__.py" and is_in_swagger_client_root:
        # Target: from .api import DefaultApi
        # Original may be: from .default_api import DefaultApi (codegen typical)
        # or from swagger_client.default_api import DefaultApi
        content = re.sub(r"from\s+(?:swagger_client\.|\.)(?:api\.)?default_api\s+import\s+DefaultApi", "from .api import DefaultApi", content)
        
        # Ensure other direct imports are single-dot relative if from swagger_client
        content = re.sub(r'from swagger_client\.api_client', 'from .api_client', content)
        content = re.sub(r'from swagger_client\.configuration', 'from .configuration', content)
        content = re.sub(r'import swagger_client\.api_client', 'import .api_client', content)
        content = re.sub(r'import swagger_client\.configuration', 'import .configuration', content)
        content = re.sub(r'from swagger_client\.models', 'from .models', content)
        content = re.sub(r'import swagger_client\.models', 'import .models', content)

    elif current_filename == "__init__.py" and is_in_api_subfolder:
        # Target: from .default_api import DefaultApi
        # Original may be: from swagger_client.api.default_api import DefaultApi (codegen typical)
        content = re.sub(r"from\s+(?:swagger_client\.api\.|\.\.api\.|\.)default_api\s+import\s+DefaultApi", "from .default_api import DefaultApi", content)

    elif current_filename == "default_api.py" and is_in_api_subfolder:
        # Imports in api/default_api.py need to go up one level for models, api_client, configuration
        # from swagger_client.models.xyz import Xyz -> from ..models.xyz import Xyz
        # from swagger_client import ApiClient -> from .. import ApiClient (or from ..api_client import ApiClient)
        content = re.sub(r'from swagger_client\.models', 'from ..models', content)
        content = re.sub(r'import swagger_client\.models', 'import ..models', content)
        content = re.sub(r'from swagger_client\.api_client import ApiClient', 'from ..api_client import ApiClient', content) # More specific
        content = re.sub(r'from swagger_client import ApiClient', 'from ..api_client import ApiClient', content) # Broader
        content = re.sub(r'from swagger_client import Configuration', 'from ..configuration import Configuration', content)
        # Also handle 'import swagger_client' if it's used for ApiClient or Configuration implicitly
        # This is less common for direct usage but good to cover if 'swagger_client.ApiClient' syntax is used
        content = re.sub(r'import swagger_client', 'import ..', content) 

    elif current_filename == "api_client.py" and is_in_swagger_client_root:
        # Imports in api_client.py (at swagger_client root)
        # from swagger_client.models.xyz import Xyz -> from .models.xyz import Xyz
        # from swagger_client.configuration import Configuration -> from .configuration import Configuration
        content = re.sub(r'from swagger_client\.models', 'from .models', content)
        content = re.sub(r'import swagger_client\.models', 'import .models', content)
        content = re.sub(r'from swagger_client\.configuration', 'from .configuration', content)
        content = re.sub(r'import swagger_client\.configuration', 'import .configuration', content)

    elif current_filename == "configuration.py" and is_in_swagger_client_root:
        # Typically, configuration.py has no swagger_client imports, but check just in case
        pass # No common patterns to fix here, usually self-contained or stdlib imports

    # General rule for model files (and other files not specifically handled)
    # This assumes they are in swagger_client/models/ or other subdirs
    elif file_path.parent.name == "models" and file_path.parent.parent == swagger_client_root:
        # from swagger_client.models.other_model import OtherModel -> from .other_model import OtherModel
        # or if a model imports another model from a different package (less common)
        # from swagger_client.xyz import Xyz -> from ..xyz import Xyz (if models is one deep)
        content = re.sub(r'from swagger_client\.models', 'from .models', content) # for sibling models
        content = re.sub(r'import swagger_client\.models', 'import .models', content)
        # If models import from top-level (e.g. configuration - unlikely but possible)
        content = re.sub(r'from swagger_client\.configuration', 'from ..configuration', content)
    
    else: # Fallback for any other files not covered explicitly, using depth-based
        try:
            relative_dir_of_file = file_path.parent.relative_to(swagger_client_root)
        except ValueError:
            print(f"Error: File {file_path} does not seem to be under swagger_client_root {swagger_client_root}")
            return
        depth = len(relative_dir_of_file.parts)
        dot_prefix = "." + "." * depth

        content = re.sub(r'from swagger_client\.([\w.]+)', rf'from {dot_prefix}.\1', content)
        content = re.sub(r'import swagger_client\.([\w.]+)', rf'import {dot_prefix}.\1', content)


    if content != original_content:
        print(f"Updating imports in: {file_path.relative_to(project_root)}")
        print_debug_info(file_path, content, "After processing, changes made")
        try:
            file_path.write_text(content, encoding='utf-8')
        except Exception as e:
            print(f"Error writing file {file_path}: {e}")
    else:
        # print_debug_info(file_path, content, "After processing, no changes") # Can be noisy
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