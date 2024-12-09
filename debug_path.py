import sys
import os
import importlib.util

print("Python executable:", sys.executable)
print("\nPython version:", sys.version)
print("\nPYTHONPATH environment variable:", os.environ.get('PYTHONPATH', 'Not set'))
print("\nsys.path:")
for path in sys.path:
    print(f"  - {path}")

# Try to find the package using importlib
def find_spec(module_name):
    try:
        spec = importlib.util.find_spec(module_name)
        if spec:
            print(f"\nFound spec for {module_name}:")
            print(f"  Origin: {spec.origin}")
            print(f"  Submodule search locations: {spec.submodule_search_locations}")
            return spec
        else:
            print(f"\nNo spec found for {module_name}")
    except Exception as e:
        print(f"\nError finding spec for {module_name}: {e}")
    return None

# Try multiple import methods
def try_import(module_name):
    print(f"\nTrying to import {module_name}:")
    try:
        # Method 1: Direct import
        module = __import__(module_name)
        print(f"  Direct import successful")
        print(f"  Module file: {module.__file__}")
        return module
    except ImportError as e:
        print(f"  Direct import failed: {e}")
    
    try:
        # Method 2: importlib import
        module = importlib.import_module(module_name)
        print(f"  Importlib import successful")
        print(f"  Module file: {module.__file__}")
        return module
    except ImportError as e:
        print(f"  Importlib import failed: {e}")
    
    return None

# Check package installation
find_spec('mcp_client_and_server')
try_import('mcp_client_and_server')
