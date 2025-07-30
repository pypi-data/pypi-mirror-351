#!/usr/bin/env python3
"""
Script to fix swagger client imports by converting absolute imports to relative imports.
This script will:
1. Find all Python files in the swagger_client directory
2. Convert all 'from swagger_client.' imports to 'from .'
3. Collapse any double occurrences of '.api.api.default_api' to '.api.default_api' and '.models.models.' to '.models.'
4. Replace any remaining absolute imports (e.g., 'from swagger_client.models.activity_feature import ...') with relative imports (e.g., 'from .models.activity_feature import ...')
5. Preserve the rest of the file content
"""

import re
from pathlib import Path
import glob

def convert_imports(file_path):
    """Convert absolute imports to relative imports in a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace all 'from swagger_client.' with 'from .'
    content = re.sub(r'from swagger_client\.', 'from .', content)

    # Handle 'import swagger_client.models' and 'from swagger_client import rest'
    content = re.sub(r'import swagger_client\.models', 'import .models', content)
    content = re.sub(r'from swagger_client import rest', 'from . import rest', content)

    # Rule for swagger_client/__init__.py: if it has an incorrect direct import of DefaultApi, point it to .api
    original_line_pattern_for_debug = r'(# import apis into sdk package\\s*\\n\\s*)from \\.default_api import DefaultApi'
    replacement_pattern_for_debug = r'\\1from .api import DefaultApi'
    
    if "swagger_client/__init__.py" in str(file_path):
        if re.search(original_line_pattern_for_debug, content):
            print(f"DEBUG: Found pattern for swagger_client/__init__.py DefaultApi import in {file_path}")
        else:
            print(f"DEBUG: DID NOT find pattern for swagger_client/__init__.py DefaultApi import in {file_path}")
            # Log a snippet of the content around where we expect the import
            try:
                idx = content.index("# import apis into sdk package")
                print(f"DEBUG: Content snippet around '# import apis into sdk package':\\n{content[max(0, idx-30):idx+100]}")
            except ValueError:
                print("DEBUG: '# import apis into sdk package' not even found.")


    content_before_sdk_fix = content
    content = re.sub(original_line_pattern_for_debug, replacement_pattern_for_debug, content)
    if "swagger_client/__init__.py" in str(file_path) and content_before_sdk_fix != content:
        print(f"DEBUG: Applied swagger_client/__init__.py DefaultApi import fix in {file_path}")
    elif "swagger_client/__init__.py" in str(file_path) and content_before_sdk_fix == content and re.search(r'from \\.api import DefaultApi', content_before_sdk_fix) is None : # only print if not already correct
        print(f"DEBUG: swagger_client/__init__.py DefaultApi import fix DID NOT change content in {file_path}")

    # Correct common problematic import pattern for DefaultApi in api/__init__.py
    content = re.sub(r'from \.api\.default_api import DefaultApi', 'from .default_api import DefaultApi', content)

    # Correct common problematic import pattern for DefaultApi in swagger_client/__init__.py
    content = re.sub(r'# import apis into sdk package\nfrom \.api\.default_api import DefaultApi', '# import apis into sdk package\nfrom .api import DefaultApi', content)

    # Collapse any double occurrences of '.api.api.default_api' to '.api.default_api' and '.models.models.' to '.models.'
    content = re.sub(r'\.api\.api\.default_api', '.api.default_api', content)
    content = re.sub(r'\.models\.models\.', '.models.', content)

    # Replace any remaining absolute imports (e.g., 'from swagger_client.models.activity_feature import ...') with relative imports (e.g., 'from .models.activity_feature import ...')
    # This specific rule is removed for now to isolate the problem
    # content = re.sub(r'from swagger_client\.models\.(\w+) import (\w+)', r'from .models.\1 import \2', content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    base_dir = Path('src/streetmanager')
    swagger_dirs = glob.glob(str(base_dir / '*/swagger_client'))
    print(f"Found swagger directories: {swagger_dirs}")
    for swagger_dir in swagger_dirs:
        swagger_path = Path(swagger_dir)
        python_files = list(swagger_path.rglob('*.py'))
        print(f"Found Python files in {swagger_path}: {python_files}")
        for file_path in python_files:
            print(f"Processing {file_path}")
            convert_imports(file_path)
            print(f"Completed {file_path}")

if __name__ == '__main__':
    main() 