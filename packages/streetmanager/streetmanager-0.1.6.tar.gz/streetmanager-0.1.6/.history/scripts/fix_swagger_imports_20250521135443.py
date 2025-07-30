#!/usr/bin/env python3
"""
Script to fix swagger client imports by converting absolute imports to relative imports.
This script will:
1. Find all Python files in the swagger_client directory
2. Convert absolute imports to relative imports (single dot for same-directory)
3. Preserve the rest of the file content
"""

import re
from pathlib import Path

def convert_imports(file_path):
    """Convert absolute imports to relative imports in a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to match: from swagger_client.models.X import Y
    pattern = r'from swagger_client\.models\.(\w+) import (\w+)'

    # Replace with: from .X import Y
    new_content = re.sub(pattern, r'from .\1 import \2', content)

    # Write the modified content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

def main():
    base_dir = Path('src/streetmanager/work/swagger_client/models')
    python_files = list(base_dir.rglob('*.py'))
    for file_path in python_files:
        print(f"Processing {file_path}")
        convert_imports(file_path)
        print(f"Completed {file_path}")

if __name__ == '__main__':
    main() 