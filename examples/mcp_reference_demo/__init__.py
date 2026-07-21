"""Runnable, synthetic-only DBOS MCP reference demo.

The package exposes a deterministic teaching flow. It is not an Agent,
Runtime, MCP connection, execution engine, permission system, or evidence
producer.
"""

from typing import Any


def run_reference_demo() -> dict[str, Any]:
    """Load the pure demo runner lazily to keep package import inert."""

    from examples.mcp_reference_demo.run_demo import (
        run_reference_demo as _run_reference_demo,
    )

    return _run_reference_demo()

__all__ = ["run_reference_demo"]
