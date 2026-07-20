"""Compatibility dispatch for pre-execution validators after a phase advances.

Legacy v0.1 validators intentionally described an empty baseline. Once the
append-only execution-chain registry records a later phase, those validators
delegate to the phase-aware validator instead of falsely requiring rollback to
the empty baseline. The frozen baseline bytes remain retained in the experiment
snapshot.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def delegate_if_advanced(root: Path, output_format: str) -> int | None:
    chain_path = root / "registry/experiment-execution-chain.yaml"
    if not chain_path.is_file():
        return None
    try:
        document = json.loads(chain_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    status = document.get("metadata", {}).get("status", "")
    phase = None
    if isinstance(status, str):
        if status.startswith("completed") or status.startswith("phase_6") or status.startswith("phase_5"):
            phase = "completed"
        elif status.startswith("phase_4"):
            phase = "authorization"
        elif status.startswith("phase_3"):
            phase = "runner"
        elif status.startswith("phase_2"):
            phase = "freeze"
        elif status.startswith("phase_1"):
            phase = "environment"
    if phase is None:
        return None
    command = [sys.executable, str(root / "validation/execution_chain_validator.py"), "--root", str(root), "--phase", phase, "--format", output_format]
    return subprocess.run(command, check=False).returncode
