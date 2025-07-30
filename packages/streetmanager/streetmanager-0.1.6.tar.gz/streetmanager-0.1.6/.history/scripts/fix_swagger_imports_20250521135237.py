#!/usr/bin/env python3
"""
Script to fix swagger client imports by converting absolute imports to relative imports.
This script will:
1. Find all Python files in the swagger_client directory
2. Convert absolute imports to relative imports
3. Preserve the rest of the file content
"""

import os
import re
from pathlib import Path

def convert_imports(file_path):
    """Convert absolute imports to relative imports in a file."""
    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to match absolute imports from swagger_client
    pattern = r'from swagger_client\.(.*?) import'
    
    # Function to convert absolute import to relative
    def replace_import(match):
        module_path = match.group(1)
        # Count the number of dots needed based on the file's depth
        depth = len(Path(file_path).relative_to('src/streetmanager/work/swagger_client').parts) - 1
        dots = '.' * depth
        return f'from {dots}models.{module_path} import'

    # Replace all absolute imports with relative ones
    new_content = re.sub(pattern, replace_import, content)
    
    # Write the modified content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

def main():
    """Main function to process all Python files in the swagger_client directory."""
    # Get the base directory for swagger_client
    base_dir = Path('src/streetmanager/work/swagger_client')
    
    # Find all Python files in the swagger_client directory
    python_files = list(base_dir.rglob('*.py'))
    
    # Process each file
    for file_path in python_files:
        print(f"Processing {file_path}")
        convert_imports(file_path)
        print(f"Completed {file_path}")

if __name__ == '__main__':
    main() 