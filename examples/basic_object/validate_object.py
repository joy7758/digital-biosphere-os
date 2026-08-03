"""Validate the synthetic quick-start Entity Object and print only the result."""

from __future__ import annotations

import json
from pathlib import Path
import sys


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from create_entity_object import build_synthetic_entity_object  # noqa: E402
from validator import validate_object  # noqa: E402


def main() -> int:
    from dbos import object_to_dict
    result = validate_object(object_to_dict(build_synthetic_entity_object()))
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
