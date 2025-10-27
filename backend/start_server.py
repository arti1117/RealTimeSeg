"""Start server script for Colab with proper path setup."""

import sys
import os

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Change to backend directory
os.chdir(backend_dir)

# Set CUDA device
os.environ['CUDA_VISIBLE_DEVICES'] = '0'

print(f"✓ Backend directory: {backend_dir}")
print(f"✓ Python path: {sys.path[0]}")
print(f"✓ Current directory: {os.getcwd()}")
print("")

# Import and run
try:
    print("Starting server...")
    from app import app, initialize_server
    import uvicorn

    # Initialize server before starting
    print("Initializing server components...")
    initialize_server()

    # Start uvicorn
    print("Starting uvicorn...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
except Exception as e:
    print(f"❌ Failed to start server: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
