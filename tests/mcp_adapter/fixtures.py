"""Synthetic in-memory inputs for the minimal MCP Tool Call adapter tests.

The values identify no real MCP server, tool, entity, context, execution, or
evidence. Tests never persist them to a DBOS registry.
"""

from __future__ import annotations

from typing import Any

from adapters.mcp import (
    SYNTHETIC_MAPPING_PROFILE_VERSION,
    SYNTHETIC_PROTOCOL_REVISION,
)


SYNTHETIC_NAMESPACE = "extension:dbos-mcp-synthetic"
SYNTHETIC_SOURCE_ID = "fixture:mcp-tool-call-adapter-v0.1"


def source_descriptor() -> dict[str, str]:
    return {
        "namespace": SYNTHETIC_NAMESPACE,
        "source_id": SYNTHETIC_SOURCE_ID,
        "version": "v0.1",
        "status": "DECLARED",
    }


def reference(
    reference_id: str,
    reference_type: str,
    *,
    source: str = SYNTHETIC_SOURCE_ID,
) -> dict[str, str]:
    return {
        "reference_id": reference_id,
        "reference_type": reference_type,
        "namespace": SYNTHETIC_NAMESPACE,
        "version": "v0.1",
        "source": source,
        "status": "DECLARED",
    }


def synthetic_tool_call(**overrides: Any) -> dict[str, Any]:
    value: dict[str, Any] = {
        "tool_call_id": "synthetic-tool-call-001",
        "tool_name": "synthetic.read_only_lookup",
        "arguments_reference": reference(
            "fixture:arguments:synthetic-tool-call-001",
            "INPUT",
        ),
        "context_reference": reference(
            "fixture:context:synthetic-tool-call-001",
            "CONTEXT",
        ),
        "source_reference": source_descriptor(),
        "entity_reference": reference(
            "fixture:entity:synthetic-caller-001",
            "ENTITY",
        ),
        "protocol_revision": SYNTHETIC_PROTOCOL_REVISION,
        "mapping_profile_version": SYNTHETIC_MAPPING_PROFILE_VERSION,
    }
    value.update(overrides)
    return value
