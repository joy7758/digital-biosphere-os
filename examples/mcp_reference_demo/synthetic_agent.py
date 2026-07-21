"""Declare the demo's synthetic Tool Call scenario without creating an Agent.

The module name describes the external-developer story only. It defines no
Agent class, identity, lifecycle, reasoning, autonomy, runtime, or execution.
The returned mapping is caller-supplied fixture data.
"""

from __future__ import annotations

from typing import Any


SYNTHETIC_NAMESPACE = "extension:dbos-mcp-synthetic"
SYNTHETIC_SOURCE_ID = "fixture:mcp-reference-demo-v0.1"


def _reference(reference_id: str, reference_type: str) -> dict[str, str]:
    return {
        "reference_id": reference_id,
        "reference_type": reference_type,
        "namespace": SYNTHETIC_NAMESPACE,
        "version": "v0.1",
        "source": SYNTHETIC_SOURCE_ID,
        "status": "DECLARED",
    }


def declare_synthetic_tool_call() -> dict[str, Any]:
    """Return one fresh Tool Call declaration with no behavioral methods."""

    return {
        "tool_call_id": "demo-synthetic-tool-call-001",
        "tool_name": "synthetic.demo.read_only_lookup",
        "arguments_reference": _reference(
            "fixture:input:demo-synthetic-tool-call-001",
            "INPUT",
        ),
        "context_reference": _reference(
            "fixture:context:demo-synthetic-tool-call-001",
            "CONTEXT",
        ),
        "source_reference": {
            "namespace": SYNTHETIC_NAMESPACE,
            "source_id": SYNTHETIC_SOURCE_ID,
            "version": "v0.1",
            "status": "DECLARED",
        },
        "entity_reference": _reference(
            "fixture:entity:demo-synthetic-caller-001",
            "ENTITY",
        ),
    }
