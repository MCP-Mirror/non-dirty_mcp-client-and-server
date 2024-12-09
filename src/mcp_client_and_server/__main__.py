import asyncio
import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from .server import main

if __name__ == "__main__":
    asyncio.run(main())
