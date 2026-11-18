from __future__ import annotations

import sys
from pathlib import Path

PHASE3_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_ROOT = PHASE3_ROOT / "scripts"
for path in (PHASE3_ROOT, SCRIPTS_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
