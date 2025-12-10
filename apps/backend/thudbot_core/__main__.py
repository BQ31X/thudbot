import sys
from pathlib import Path

# Add project root to sys.path BEFORE importing anything from thudbot_core
# This must happen before any imports that might need rag_utils
backend_dir = Path(__file__).resolve().parent.parent
project_root = backend_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Now safe to import (rag_utils is on sys.path)
import uvicorn
from thudbot_core.config import load_env

if __name__ == "__main__":
    load_env()  # Load .env variables before starting
    uvicorn.run("thudbot_core.api:app", host="0.0.0.0", port=8000, reload=True)
