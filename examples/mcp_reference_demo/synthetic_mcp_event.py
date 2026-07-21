"""Build one strict synthetic MCP-style Tool Call fixture.

This is an in-memory test input, not an observed MCP event, protocol message,
server request, transport record, execution fact, or evidence object.
"""

from __future__ import annotations

from typing import Any

from adapters.mcp import (
    SYNTHETIC_MAPPING_PROFILE_VERSION,
    SYNTHETIC_PROTOCOL_REVISION,
)
from examples.mcp_reference_demo.synthetic_agent import (
    declare_synthetic_tool_call,
)


def build_synthetic_mcp_tool_call_event() -> dict[str, Any]:
    """Add exact DBOS synthetic profile fields to a fresh scenario mapping."""

    event = declare_synthetic_tool_call()
    event.update(
        {
            "protocol_revision": SYNTHETIC_PROTOCOL_REVISION,
            "mapping_profile_version": SYNTHETIC_MAPPING_PROFILE_VERSION,
        }
    )
    return event
