#!/usr/bin/env python3
"""
Script to fix swagger client imports by converting absolute imports to relative imports.
This script will:
1. Find all Python files in the swagger_client directory
2. Convert all 'from swagger_client.' imports to 'from .'
3. Collapse any double occurrences of '.api.api.' to '.api.' and '.models.models.' to '.models.'
4. Replace any remaining absolute imports (e.g., 'from swagger_client.models.activity_feature import ...') with relative imports (e.g., 'from .models.activity_feature import ...')
5. Preserve the rest of the file content
"""

import re
from pathlib import Path

def convert_imports(file_path):
    """Convert absolute imports to relative imports in a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace all 'from swagger_client.' with 'from .'
    content = re.sub(r'from swagger_client\.', 'from .', content)

    # Collapse any double occurrences of '.api.api.' to '.api.' and '.models.models.' to '.models.'
    content = re.sub(r'\.api\.api\.', '.api.', content)
    content = re.sub(r'\.models\.models\.', '.models.', content)

    # Replace any remaining absolute imports (e.g., 'from swagger_client.models.activity_feature import ...') with relative imports (e.g., 'from .models.activity_feature import ...')
    content = re.sub(r'from swagger_client\.models\.(\w+) import (\w+)', r'from .models.\1 import \2', content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    base_dir = Path('src/streetmanager/*/')
    python_files = list(base_dir.rglob('*.py'))
    for file_path in python_files:
        print(f"Processing {file_path}")
        convert_imports(file_path)
        print(f"Completed {file_path}")

if __name__ == '__main__':
    main() 