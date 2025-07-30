#!/usr/bin/env python3
"""
Script to fix swagger client imports by converting absolute imports to relative imports.
This script will:
1. Find all Python files in the swagger_client directory
2. Convert all 'from swagger_client.' imports to 'from .'
3. Ensure all model-to-model imports are 'from .X import Y'
4. Preserve the rest of the file content
"""

import re
from pathlib import Path

def convert_imports(file_path):
    """Convert absolute imports to relative imports in a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace all 'from swagger_client.' with 'from .'
    content = re.sub(r'from swagger_client\.', 'from .', content)

    # For model files, ensure model-to-model imports are 'from .X import Y'
    # (This is already handled by the above, but we keep this for clarity)
    content = re.sub(r'from \.models\.(\w+) import (\w+)', r'from .\1 import \2', content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    base_dir = Path('src/streetmanager/*/swagger_client')
    python_files = list(base_dir.rglob('*.py'))
    for file_path in python_files:
        print(f"Processing {file_path}")
        convert_imports(file_path)
        print(f"Completed {file_path}")

if __name__ == '__main__':
    main() 