"""
conftest.py
-----------
Makes the backend/ directory importable as top-level modules (config,
core.*, tools.*) when running pytest from anywhere, matching how
uvicorn runs main.py from inside backend/.
"""

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
