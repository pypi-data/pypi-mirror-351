#!/usr/bin/env python3

import os
import re

def fix_imports_in_file(file_path):
    """Fix imports in a single file by replacing absolute imports with relative ones."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace absolute imports with relative imports
    modified_content = re.sub(
        r'from swagger_client\.models\.(\w+) import',
        r'from .\1 import',
        content
    )
    
    if content != modified_content:
        with open(file_path, 'w') as f:
            f.write(modified_content)
        print(f"Fixed imports in {file_path}")
    else:
        print(f"No changes needed in {file_path}")

def main():
    """Main function to fix imports in all model files."""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the models directory
    models_dir = os.path.join(script_dir, 'swagger_client', 'models')
    
    # Walk through all Python files in the models directory
    for root, _, files in os.walk(models_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                fix_imports_in_file(file_path)

if __name__ == '__main__':
    main() 