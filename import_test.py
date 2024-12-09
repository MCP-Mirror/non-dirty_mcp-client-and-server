import sys
import os

# Print current working directory
print("Current working directory:", os.getcwd())

# Add the src directory to Python path
src_dir = os.path.join(os.getcwd(), 'src')
sys.path.insert(0, src_dir)
print("\nAdded to sys.path:", src_dir)

# Print sys.path
print("\nUpdated sys.path:")
for path in sys.path:
    print(f"  - {path}")

# Try to import
try:
    import mcp_client_and_server
    print("\nSuccessfully imported mcp_client_and_server")
    print("Module location:", mcp_client_and_server.__file__)
except ImportError as e:
    print("\nFailed to import mcp_client_and_server:", str(e))
    
# Try to import specific modules
try:
    from mcp_client_and_server import server
    print("\nSuccessfully imported server module")
    print("Server module location:", server.__file__)
except ImportError as e:
    print("\nFailed to import server module:", str(e))
