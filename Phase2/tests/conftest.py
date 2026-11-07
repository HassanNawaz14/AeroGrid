from __future__ import annotations

import sys
from pathlib import Path

# Ensure `import etl...` resolves when running pytest from repo root or Phase2.
PHASE2_ROOT = Path(__file__).resolve().parents[1]
if str(PHASE2_ROOT) not in sys.path:
    sys.path.insert(0, str(PHASE2_ROOT))
