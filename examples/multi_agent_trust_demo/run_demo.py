#!/usr/bin/env python3
"""Print the deterministic Multi-Agent Trust Demo as JSON."""

from __future__ import annotations

import json

from examples.multi_agent_trust_demo.demo import build_demo


def main() -> int:
    result = build_demo()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["demo_contract_satisfied"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
